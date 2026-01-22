#!/bin/bash
# Compile TikZ .tex file to PNG
# Usage: ./compile_tikz.sh figure.tex [dpi]
#
# Requires: pdflatex (TeX Live), ImageMagick (magick command)

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <file.tex> [dpi]"
    echo "  dpi: Resolution for PNG output (default: 300)"
    exit 1
fi

TEX_FILE="$1"
DPI="${2:-300}"
BASE_NAME="${TEX_FILE%.tex}"

if [ ! -f "$TEX_FILE" ]; then
    echo "Error: File not found: $TEX_FILE"
    exit 1
fi

echo "Compiling $TEX_FILE..."

# Compile LaTeX to PDF
pdflatex -interaction=nonstopmode "$TEX_FILE" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "LaTeX compilation failed. Running again for error output:"
    pdflatex -interaction=nonstopmode "$TEX_FILE" | tail -20
    exit 1
fi

echo "Converting to PNG at ${DPI} DPI..."

# Convert PDF to PNG
magick -density "$DPI" "${BASE_NAME}.pdf" -quality 95 "${BASE_NAME}.png"

# Clean up auxiliary files (keep PDF for vector output)
rm -f "${BASE_NAME}.aux" "${BASE_NAME}.log"

echo "Created: ${BASE_NAME}.pdf and ${BASE_NAME}.png"
ls -lh "${BASE_NAME}.pdf" "${BASE_NAME}.png"
