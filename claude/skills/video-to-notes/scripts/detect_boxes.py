#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "opencv-python>=4.8.0",
#     "numpy>=1.24.0",
# ]
# ///
"""
detect-boxes: Detect and label rectangular bounding boxes in images for LLM selection.

Usage:
    detect-boxes input.png                          # Detect boxes, output to input_boxes.png
    detect-boxes input.png -o annotated.png         # Specify output
    detect-boxes input.png --json                   # Output box coordinates as JSON
    detect-boxes input.png --crop A -o cropped.png  # Crop to box A
    detect-boxes input.png --crop A+B -p 20         # Crop spanning A and B with padding
    detect-boxes input.png --crop A:C -p 10,20      # Crop spanning A through C

Box selection formats:
    A           # Single box
    A+B         # Span boxes A and B (bounding box containing both)
    A:C         # Span A through C (all boxes in range)

Padding formats (CSS-style):
    --padding 20              # 20px on all sides
    --padding 10,30           # 10px top/bottom, 30px left/right
    --padding 10,20,30,40     # top, right, bottom, left

Detects rectangular borders (plot frames, figure boundaries) using edge detection.
For images without clear borders, use overlay_grid.py instead.
"""

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np


def detect_rectangles(
    image: np.ndarray,
    min_area_ratio: float = 0.01,
    max_area_ratio: float = 0.95,
    keep_nested: bool = False,
) -> list[tuple[int, int, int, int]]:
    """
    Detect rectangular bounding boxes in an image.

    Returns list of (x, y, w, h) tuples sorted by area (largest first).
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Edge detection
    edges = cv2.Canny(gray, 50, 150)

    # Dilate to close gaps in edges
    kernel = np.ones((3, 3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)

    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    img_area = image.shape[0] * image.shape[1]
    min_area = img_area * min_area_ratio
    max_area = img_area * max_area_ratio

    rectangles = []
    for contour in contours:
        # Approximate contour to polygon
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Check if it's roughly rectangular (4 corners)
        if len(approx) >= 4:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h

            # Filter by size
            if min_area < area < max_area:
                # Filter by aspect ratio (not too thin)
                aspect = max(w, h) / min(w, h) if min(w, h) > 0 else float("inf")
                if aspect < 10:
                    rectangles.append((x, y, w, h))

    # Remove duplicates (overlapping boxes), optionally keeping nested ones
    rectangles = dedupe_boxes(rectangles, keep_nested=keep_nested)

    # Sort by area (largest first)
    rectangles.sort(key=lambda r: r[2] * r[3], reverse=True)

    return rectangles


def dedupe_boxes(
    boxes: list[tuple[int, int, int, int]],
    overlap_thresh: float = 0.8,
    keep_nested: bool = False,
) -> list[tuple[int, int, int, int]]:
    """
    Remove boxes that overlap significantly with larger boxes.

    If keep_nested=True, keeps boxes that are fully contained within larger boxes
    (useful for detecting sub-elements like inner plots within slides).
    """
    if not boxes:
        return []

    # Sort by area descending
    sorted_boxes = sorted(boxes, key=lambda b: b[2] * b[3], reverse=True)
    keep = []

    for box in sorted_boxes:
        x1, y1, w1, h1 = box
        is_duplicate = False

        for kept in keep:
            x2, y2, w2, h2 = kept

            # Calculate intersection
            ix1 = max(x1, x2)
            iy1 = max(y1, y2)
            ix2 = min(x1 + w1, x2 + w2)
            iy2 = min(y1 + h1, y2 + h2)

            if ix1 < ix2 and iy1 < iy2:
                intersection = (ix2 - ix1) * (iy2 - iy1)
                box_area = w1 * h1

                if intersection / box_area > overlap_thresh:
                    # Check if this box is fully nested inside the kept box
                    is_fully_nested = (
                        x1 >= x2 and y1 >= y2 and
                        x1 + w1 <= x2 + w2 and y1 + h1 <= y2 + h2
                    )

                    if keep_nested and is_fully_nested:
                        # Keep nested boxes as separate elements
                        pass
                    else:
                        is_duplicate = True
                        break

        if not is_duplicate:
            keep.append(box)

    return keep


def index_to_label(idx: int) -> str:
    """Convert index to letter label (0=A, 25=Z, 26=AA, etc.)."""
    result = ""
    idx += 1
    while idx > 0:
        idx -= 1
        result = chr(ord("A") + (idx % 26)) + result
        idx //= 26
    return result


def label_to_index(label: str) -> int:
    """Convert letter label to index (A=0, Z=25, AA=26, etc.)."""
    result = 0
    for char in label.upper():
        result = result * 26 + (ord(char) - ord("A") + 1)
    return result - 1


def annotate_image(
    image: np.ndarray,
    boxes: list[tuple[int, int, int, int]],
    color: tuple[int, int, int] = (0, 0, 255),  # BGR red
    thickness: int = 2,
) -> np.ndarray:
    """Draw labeled boxes on image."""
    annotated = image.copy()

    for i, (x, y, w, h) in enumerate(boxes):
        label = index_to_label(i)

        # Draw rectangle
        cv2.rectangle(annotated, (x, y), (x + w, y + h), color, thickness)

        # Draw label background
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.8
        font_thickness = 2
        (text_w, text_h), baseline = cv2.getTextSize(label, font, font_scale, font_thickness)

        # Position label at top-left of box
        label_x = x + 5
        label_y = y + text_h + 10

        # Draw background rectangle
        cv2.rectangle(
            annotated,
            (label_x - 2, label_y - text_h - 2),
            (label_x + text_w + 2, label_y + baseline + 2),
            (255, 255, 255),
            -1,
        )

        # Draw text
        cv2.putText(annotated, label, (label_x, label_y), font, font_scale, color, font_thickness)

    return annotated


def parse_box_selection(selection: str, num_boxes: int) -> list[int]:
    """
    Parse box selection string into list of box indices.

    Formats:
        "A"     -> [0]
        "A+B"   -> [0, 1]
        "A:C"   -> [0, 1, 2]
        "A+C"   -> [0, 2]
    """
    selection = selection.upper().strip()

    # Range format: A:C
    if ":" in selection:
        parts = selection.split(":")
        if len(parts) != 2:
            raise ValueError(f"Invalid range format: {selection}")
        start = label_to_index(parts[0].strip())
        end = label_to_index(parts[1].strip())
        if start > end:
            start, end = end, start
        indices = list(range(start, end + 1))

    # Multi-select format: A+B+C
    elif "+" in selection:
        parts = selection.split("+")
        indices = [label_to_index(p.strip()) for p in parts]

    # Single box: A
    else:
        indices = [label_to_index(selection)]

    # Validate indices
    for idx in indices:
        if idx < 0 or idx >= num_boxes:
            raise ValueError(f"Box {index_to_label(idx)} not found (have {num_boxes} boxes: A-{index_to_label(num_boxes-1)})")

    return indices


def compute_spanning_box(
    boxes: list[tuple[int, int, int, int]], indices: list[int]
) -> tuple[int, int, int, int]:
    """Compute bounding box that spans all selected boxes."""
    selected = [boxes[i] for i in indices]

    min_x = min(b[0] for b in selected)
    min_y = min(b[1] for b in selected)
    max_x = max(b[0] + b[2] for b in selected)
    max_y = max(b[1] + b[3] for b in selected)

    return (min_x, min_y, max_x - min_x, max_y - min_y)


def parse_padding(padding_str: str) -> tuple[int, int, int, int]:
    """
    Parse CSS-style padding string into (top, right, bottom, left) pixels.
    """
    values = [int(v.strip()) for v in padding_str.split(",")]

    if len(values) == 1:
        return (values[0], values[0], values[0], values[0])
    elif len(values) == 2:
        return (values[0], values[1], values[0], values[1])
    elif len(values) == 4:
        return tuple(values)  # type: ignore
    else:
        raise ValueError(
            f"Invalid padding '{padding_str}'. Use 1, 2, or 4 values: "
            "'20' or '10,30' or '10,20,30,40'"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect and label rectangular bounding boxes in images.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s screenshot.png                    # Detect and label boxes
    %(prog)s screenshot.png --json             # Output box coordinates
    %(prog)s screenshot.png --crop A           # Crop to box A
    %(prog)s screenshot.png --crop A+B -p 20   # Crop spanning A and B with padding
    %(prog)s screenshot.png --crop A:C         # Crop spanning A through C

Box selection:
    A       Single box
    A+B     Span boxes A and B
    A:C     Span A through C (all boxes in range)

For images without clear borders, use overlay_grid.py instead.
        """,
    )
    parser.add_argument("input", type=Path, help="Input image file")
    parser.add_argument("-o", "--output", type=Path, help="Output file")
    parser.add_argument("--json", action="store_true", help="Output box coordinates as JSON")
    parser.add_argument(
        "--crop",
        type=str,
        metavar="BOXES",
        help="Crop to selected box(es): A, A+B, or A:C",
    )
    parser.add_argument(
        "-p",
        "--padding",
        type=str,
        metavar="PIXELS",
        help="Padding around crop (CSS-style): '20', '10,30', or '10,20,30,40'",
    )
    parser.add_argument(
        "--min-area",
        type=float,
        default=0.01,
        help="Minimum box area as fraction of image (default: 0.01)",
    )
    parser.add_argument(
        "--max-area",
        type=float,
        default=0.95,
        help="Maximum box area as fraction of image (default: 0.95)",
    )
    parser.add_argument(
        "--keep-nested",
        action="store_true",
        help="Keep boxes nested inside larger boxes (for sub-elements like inner plots)",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1

    # Load image
    image = cv2.imread(str(args.input))
    if image is None:
        print(f"Error: Could not read image: {args.input}", file=sys.stderr)
        return 1

    height, width = image.shape[:2]

    # Detect boxes
    boxes = detect_rectangles(image, args.min_area, args.max_area, args.keep_nested)

    if not boxes:
        print("No rectangular boxes detected. Try overlay_grid.py instead.", file=sys.stderr)
        return 1

    print(f"Detected {len(boxes)} box(es)", file=sys.stderr)

    # Crop mode
    if args.crop:
        try:
            indices = parse_box_selection(args.crop, len(boxes))
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

        x, y, w, h = compute_spanning_box(boxes, indices)

        # Apply padding
        if args.padding:
            try:
                pad_top, pad_right, pad_bottom, pad_left = parse_padding(args.padding)
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
                return 1

            x = max(0, x - pad_left)
            y = max(0, y - pad_top)
            w = min(width - x, w + pad_left + pad_right)
            h = min(height - y, h + pad_top + pad_bottom)

        # Crop
        cropped = image[y : y + h, x : x + w]

        output_path = args.output or args.input.parent / f"{args.input.stem}_cropped{args.input.suffix}"
        cv2.imwrite(str(output_path), cropped)

        padding_info = f" +padding {args.padding}" if args.padding else ""
        print(f"Cropped {args.crop}{padding_info} -> ({x},{y})-({x+w},{y+h}): {output_path}", file=sys.stderr)
        return 0

    # Detection/annotation mode
    annotated = annotate_image(image, boxes)

    output_path = args.output or args.input.parent / f"{args.input.stem}_boxes.png"
    cv2.imwrite(str(output_path), annotated)
    print(f"Annotated: {output_path}", file=sys.stderr)

    # JSON output
    if args.json:
        box_data = {
            "image_width": width,
            "image_height": height,
            "boxes": [
                {
                    "label": index_to_label(i),
                    "x": x,
                    "y": y,
                    "width": w,
                    "height": h,
                }
                for i, (x, y, w, h) in enumerate(boxes)
            ],
        }
        print(json.dumps(box_data, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
