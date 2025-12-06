"""
speak - Text-to-speech utility using Kokoro ONNX with queue support

Usage:
    # Direct mode (immediate playback)
    speak "Hello world"
    speak "Hello world" --voice af_sarah
    echo "Hello world" | speak

    # Multi-chunk queue mode (zero-lag playback)
    # Each line is treated as a separate chunk
    cat <<'EOF' | speak --queue
    The test suite finished. Twenty three tests passed.
    Two tests failed in the authentication module.
    Both failures are timeout related.
    Looks like a mock configuration issue.
    EOF
"""

import sys
import io
import os
import subprocess
import argparse
import json
import time
import signal
import threading
import socket
import fcntl
from pathlib import Path
from urllib.request import urlretrieve
from multiprocessing import Process
from queue import Queue as ThreadQueue, Empty
from typing import Tuple

import soundfile as sf
from kokoro_onnx import Kokoro


# Default model directory
MODEL_DIR = Path.home() / ".local/share/kokoro-onnx"
MODEL_FILE = MODEL_DIR / "kokoro-v1.0.onnx"
VOICES_FILE = MODEL_DIR / "voices-v1.0.bin"

# Queue directory
QUEUE_DIR = Path.home() / ".local/share/speak"
PID_FILE = QUEUE_DIR / "worker.pid"
SOCKET_FILE = QUEUE_DIR / "worker.sock"
LOCK_FILE = QUEUE_DIR / "worker.lock"
LOG_FILE = QUEUE_DIR / "worker.log"
QUEUE_TIMEOUT = 30  # Auto-stop worker after 30s idle
MAX_CONCURRENT_CONNECTIONS = 24  # Limit concurrent socket connections

# Download URLs
MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"

DEFAULT_VOICE = "am_echo"
DEFAULT_SPEED = 1.0
DEFAULT_LANG = "en-us"

# Global verbose flag
VERBOSE = False

def log(msg: str) -> None:
    """Log message if verbose mode is enabled"""
    if VERBOSE:
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {msg}", file=sys.stderr)


def download_file(url: str, dest: Path, desc: str) -> None:
    """Download a file with progress indication"""
    print(f"Downloading {desc}...", file=sys.stderr)
    print(f"  From: {url}", file=sys.stderr)
    print(f"  To: {dest}", file=sys.stderr)

    def report_progress(block_num: int, block_size: int, total_size: int) -> None:
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100, downloaded * 100 / total_size)
            mb_downloaded = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            print(f"\r  Progress: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)",
                  end='', file=sys.stderr)

    try:
        urlretrieve(url, str(dest), reporthook=report_progress)
        print(file=sys.stderr)  # New line after progress
        print(f"✓ Downloaded {desc}", file=sys.stderr)
    except Exception as e:
        print(f"\n✗ Failed to download {desc}: {e}", file=sys.stderr)
        raise


def ensure_models() -> Tuple[str, str]:
    """Ensure models are downloaded, download if necessary"""
    if MODEL_FILE.exists() and VOICES_FILE.exists():
        return str(MODEL_FILE), str(VOICES_FILE)

    # Models don't exist, download them
    print("=" * 60, file=sys.stderr)
    print("Kokoro models not found. Downloading (~340 MB)...", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    if not MODEL_FILE.exists():
        download_file(MODEL_URL, MODEL_FILE, "kokoro-v1.0.onnx")

    if not VOICES_FILE.exists():
        download_file(VOICES_URL, VOICES_FILE, "voices-v1.0.bin")

    print("=" * 60, file=sys.stderr)
    print(f"✓ Models installed to {MODEL_DIR}", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    return str(MODEL_FILE), str(VOICES_FILE)


def generate_audio(text: str, voice: str, speed: float, lang: str,
                   model_path: str, voices_path: str) -> bytes:
    """Generate audio and return as WAV bytes"""
    kokoro = Kokoro(model_path, voices_path)
    samples, sample_rate = kokoro.create(text, voice=voice, speed=speed, lang=lang)

    buffer = io.BytesIO()
    sf.write(buffer, samples, sample_rate, format='WAV')
    buffer.seek(0)
    return buffer.read()


def speak_text(text: str, voice: str, speed: float, lang: str,
         model_path: str, voices_path: str) -> None:
    """Generate and play speech immediately"""
    audio_bytes = generate_audio(text, voice, speed, lang, model_path, voices_path)
    play_audio(audio_bytes)


def play_audio(audio_bytes: bytes, chunk_info: str = "") -> None:
    """Play audio bytes via ffplay"""
    log(f"Playing audio {chunk_info}")
    start_time = time.time()
    proc = subprocess.Popen(
        ['ffplay', '-nodisp', '-autoexit', '-f', 'wav', '-i', 'pipe:0'],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    proc.communicate(input=audio_bytes)
    duration = time.time() - start_time
    log(f"Completed playing {chunk_info} ({duration:.2f}s)")


def worker_process(model_path, voices_path):
    """Background worker process with threading for parallel generation and playback"""
    audio_buffer = ThreadQueue(maxsize=3)  # Buffer up to 3 chunks
    msg_queue = ThreadQueue()  # Internal message queue
    shutdown_event = threading.Event()
    last_activity = [time.time()]  # Mutable for thread sharing
    connection_semaphore = threading.Semaphore(MAX_CONCURRENT_CONNECTIONS)

    # Signal handling for clean shutdown
    def signal_handler(signum, frame):
        shutdown_event.set()
        msg_queue.put(None)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    def handle_connection(conn):
        """Handle a single socket connection"""
        try:
            data = b''
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                data += chunk

            if data:
                try:
                    msg = json.loads(data.decode('utf-8'))
                    msg_queue.put(msg)
                    last_activity[0] = time.time()
                    conn.sendall(b'OK')
                except json.JSONDecodeError:
                    conn.sendall(b'ERROR')
        finally:
            conn.close()
            connection_semaphore.release()  # Release slot

    def socket_listener():
        """Listen for messages on Unix socket"""
        sock = None
        try:
            # Create socket
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.bind(str(SOCKET_FILE))
            sock.listen(10)  # Increased backlog for concurrent connections
            sock.settimeout(1.0)  # Timeout for checking shutdown

            while not shutdown_event.is_set():
                try:
                    conn, _ = sock.accept()

                    # Acquire semaphore slot (blocks if at limit)
                    if not connection_semaphore.acquire(blocking=False):
                        # Too many connections, reject
                        try:
                            conn.sendall(b'BUSY')
                            conn.close()
                        except:
                            pass
                        continue

                    # Handle connection in separate thread
                    handler = threading.Thread(target=handle_connection, args=(conn,), daemon=True)
                    handler.start()
                except socket.timeout:
                    # Check for idle timeout
                    if time.time() - last_activity[0] > QUEUE_TIMEOUT:
                        shutdown_event.set()
                        msg_queue.put(None)  # Signal generator to stop
                    continue
                except Exception as e:
                    # Log error but continue listening
                    print(f"Socket error: {e}", file=sys.stderr)
                    continue
        finally:
            if sock:
                sock.close()
            SOCKET_FILE.unlink(missing_ok=True)

    def generator_thread():
        """Generate audio from messages and add to buffer"""
        chunk_num = [0]  # Mutable for closure
        while not shutdown_event.is_set():
            try:
                msg = msg_queue.get(timeout=1)
                if msg is None:  # Shutdown signal
                    audio_buffer.put((None, ""))
                    break

                # Generate audio
                try:
                    chunk_num[0] += 1
                    chunk_info = f"chunk #{chunk_num[0]}: '{msg['text'][:30]}...'"
                    log(f"Generating {chunk_info}")
                    start_time = time.time()

                    audio_bytes = generate_audio(
                        msg['text'], msg['voice'], msg['speed'],
                        msg['lang'], model_path, voices_path
                    )

                    duration = time.time() - start_time
                    log(f"Generated {chunk_info} ({duration:.2f}s)")

                    # Add to playback buffer with info
                    audio_buffer.put((audio_bytes, chunk_info))
                except Exception as e:
                    # Log generation error but continue processing
                    print(f"Generation error: {e}", file=sys.stderr)
                    continue

            except Empty:
                continue

    def player_thread():
        """Play audio from buffer"""
        while not shutdown_event.is_set():
            try:
                item = audio_buffer.get(timeout=1)
                if item[0] is None:  # Shutdown signal
                    break
                audio_bytes, chunk_info = item
                try:
                    play_audio(audio_bytes, chunk_info)
                except Exception as e:
                    # Log playback error but continue processing
                    print(f"Playback error: {e}", file=sys.stderr)
                    continue
            except Empty:
                continue

    # Start all threads
    socket_thread = threading.Thread(target=socket_listener, daemon=True)
    gen_thread = threading.Thread(target=generator_thread, daemon=True)
    play_thread = threading.Thread(target=player_thread, daemon=True)

    socket_thread.start()
    gen_thread.start()
    play_thread.start()

    # Wait for threads to complete
    socket_thread.join()
    gen_thread.join()
    play_thread.join()

    # Cleanup
    cleanup_worker()


def is_worker_running():
    """Check if worker process is running"""
    if not PID_FILE.exists():
        return False

    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())

        # Check if process exists
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        # Process doesn't exist or PID file is invalid
        PID_FILE.unlink(missing_ok=True)
        return False


def start_worker(model_path, voices_path):
    """Start background worker process with file locking to prevent race conditions"""
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)

    # Use file locking to prevent multiple workers from starting
    lock_file = open(LOCK_FILE, 'w')
    try:
        # Try to acquire exclusive lock (non-blocking)
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

        # Check again if worker is running (another process may have started it)
        if is_worker_running():
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            lock_file.close()
            return None

        # Clean up old socket if it exists
        SOCKET_FILE.unlink(missing_ok=True)

        # Start worker process
        worker = Process(
            target=worker_process,
            args=(model_path, voices_path),
            daemon=False  # Not daemon so it can outlive parent
        )
        worker.start()

        # Save PID
        with open(PID_FILE, 'w') as f:
            f.write(str(worker.pid))

        # Wait for socket to be created
        for _ in range(50):  # Wait up to 5 seconds
            if SOCKET_FILE.exists():
                break
            time.sleep(0.1)

        # Release lock
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        lock_file.close()

        return worker

    except BlockingIOError:
        # Another process is starting the worker, wait for it
        lock_file.close()
        for _ in range(50):
            if is_worker_running() and SOCKET_FILE.exists():
                return None
            time.sleep(0.1)
        return None


def cleanup_worker():
    """Cleanup worker process files"""
    PID_FILE.unlink(missing_ok=True)
    SOCKET_FILE.unlink(missing_ok=True)


def send_to_queue(text, voice, speed, lang, model_path, voices_path):
    """Send message to queue (client mode)"""
    start_time = time.time()
    log(f"Client: Starting send_to_queue for '{text[:30]}...'")

    # Start worker if not running
    if not is_worker_running():
        log("Client: Worker not running, starting...")
        start_worker(model_path, voices_path)
        log(f"Client: Worker started ({time.time() - start_time:.3f}s)")

    # Send message via Unix socket
    msg = {
        'text': text,
        'voice': voice,
        'speed': speed,
        'lang': lang
    }

    # Retry logic for connection
    max_retries = 3
    for attempt in range(max_retries):
        try:
            log(f"Client: Connecting to socket (attempt {attempt + 1})")
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(5.0)  # 5 second timeout

            connect_start = time.time()
            sock.connect(str(SOCKET_FILE))
            log(f"Client: Connected ({time.time() - connect_start:.3f}s)")

            send_start = time.time()
            sock.sendall(json.dumps(msg).encode('utf-8'))
            sock.shutdown(socket.SHUT_WR)
            log(f"Client: Sent message ({time.time() - send_start:.3f}s)")

            recv_start = time.time()
            response = sock.recv(10)
            log(f"Client: Received response ({time.time() - recv_start:.3f}s)")
            sock.close()

            log(f"Client: Total time {time.time() - start_time:.3f}s")

            if response == b'OK':
                return True
            elif response == b'ERROR':
                print("Worker reported error processing message", file=sys.stderr)
                return False

        except FileNotFoundError:
            # Socket doesn't exist, worker may have crashed
            if attempt < max_retries - 1:
                print("Worker socket not found, restarting worker...", file=sys.stderr)
                cleanup_worker()
                start_worker(model_path, voices_path)
                time.sleep(0.5)
                continue
            else:
                print("Failed to connect to worker after retries", file=sys.stderr)
                return False

        except socket.timeout:
            print(f"Connection timeout (attempt {attempt + 1}/{max_retries})", file=sys.stderr)
            if attempt < max_retries - 1:
                time.sleep(0.5)
                continue
            return False

        except Exception as e:
            print(f"Error sending to queue: {e}", file=sys.stderr)
            if attempt < max_retries - 1:
                time.sleep(0.5)
                continue
            return False

    return False


def main():
    parser = argparse.ArgumentParser(
        description='Text-to-speech using Kokoro ONNX',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  speak "Hello world"
  speak "Hello world" --voice am_adam
  speak "Hello world" -v af_nova --speed 1.2
  echo "This is a test" | speak

Popular voices:
  American female: af_sarah, af_river, af_bella
  American male: am_echo, am_puck, am_liam
  British female: bf_alice, bf_emma
  British male: bm_fable, bm_daniel
        """
    )

    parser.add_argument(
        'text',
        nargs='?',
        help='Text to speak (reads from stdin if not provided)'
    )
    parser.add_argument(
        '-v', '--voice',
        default=DEFAULT_VOICE,
        help=f'Voice to use (default: {DEFAULT_VOICE})'
    )
    parser.add_argument(
        '-s', '--speed',
        type=float,
        default=DEFAULT_SPEED,
        help=f'Speech speed (default: {DEFAULT_SPEED})'
    )
    parser.add_argument(
        '-l', '--lang',
        default=DEFAULT_LANG,
        help=f'Language code (default: {DEFAULT_LANG})'
    )
    parser.add_argument(
        '--model-path',
        help='Path to kokoro-v1.0.onnx (auto-detected if not provided)'
    )
    parser.add_argument(
        '--voices-path',
        help='Path to voices-v1.0.bin (auto-detected if not provided)'
    )
    parser.add_argument(
        '--list-voices',
        action='store_true',
        help='List all available voices and exit'
    )
    parser.add_argument(
        '--queue',
        action='store_true',
        help='Use queue mode for zero-lag multi-chunk playback'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging for debugging'
    )

    args = parser.parse_args()

    # Set global verbose flag
    global VERBOSE
    VERBOSE = args.verbose

    # Get model paths - download if necessary
    if args.model_path and args.voices_path:
        model_path = args.model_path
        voices_path = args.voices_path
    else:
        try:
            model_path, voices_path = ensure_models()
        except Exception as e:
            print(f"Error: Failed to ensure models are available: {e}", file=sys.stderr)
            sys.exit(1)

    # List voices if requested
    if args.list_voices:
        kokoro = Kokoro(model_path, voices_path)
        voices = kokoro.get_voices()

        # Group by category
        categories = {
            'American Female': [v for v in voices if v.startswith('af_')],
            'American Male': [v for v in voices if v.startswith('am_')],
            'British Female': [v for v in voices if v.startswith('bf_')],
            'British Male': [v for v in voices if v.startswith('bm_')],
            'Other': [v for v in voices if not v.startswith(('af_', 'am_', 'bf_', 'bm_'))]
        }

        for category, category_voices in categories.items():
            if category_voices:
                print(f"\n{category}:")
                for voice in sorted(category_voices):
                    print(f"  {voice}")
        sys.exit(0)

    # Get text from args or stdin
    if args.text:
        texts = [args.text]
    else:
        if sys.stdin.isatty():
            print("Error: No text provided. Use as argument or pipe from stdin.", file=sys.stderr)
            print("Try: speak --help", file=sys.stderr)
            sys.exit(1)
        # In queue mode, treat each line as a separate chunk
        # In direct mode, treat all input as one chunk
        stdin_content = sys.stdin.read().strip()
        if args.queue:
            # Split by newlines for multiple chunks
            texts = [line.strip() for line in stdin_content.split('\n') if line.strip()]
        else:
            texts = [stdin_content]

    if not texts or not any(texts):
        print("Error: Empty text provided.", file=sys.stderr)
        sys.exit(1)

    # Queue mode or direct mode
    try:
        if args.queue:
            # Send all chunks to queue for parallel processing
            for i, text in enumerate(texts):
                log(f"Queuing chunk {i+1}/{len(texts)}")
                success = send_to_queue(text, args.voice, args.speed, args.lang, model_path, voices_path)
                if not success:
                    print(f"Failed to queue chunk {i+1}", file=sys.stderr)
                    sys.exit(1)
            log(f"Successfully queued {len(texts)} chunk(s)")
        else:
            # Direct mode - immediate playback (only first text)
            speak_text(texts[0], args.voice, args.speed, args.lang, model_path, voices_path)
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
