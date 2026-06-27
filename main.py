import argparse
import sys
import time
import urllib.parse
import urllib.request


REQUEST_COUNT = 10
CHUNK_SIZE = 1024 * 1024


def download(url):
    request = urllib.request.Request(
        url,
        headers={
            "Accept-Encoding": "identity",
            "User-Agent": "speed-test/1.0",
        },
    )
    downloaded = 0
    started_at = time.perf_counter()

    with urllib.request.urlopen(request, timeout=30) as response:
        while chunk := response.read(CHUNK_SIZE):
            downloaded += len(chunk)

    return downloaded, time.perf_counter() - started_at


def calculate_speed(downloaded_bytes, elapsed_seconds):
    return downloaded_bytes / elapsed_seconds / 1_000_000


def self_test():
    assert calculate_speed(10_000_000, 2) == 5


def main():
    parser = argparse.ArgumentParser(
        description="Measures sequential file download speed."
    )
    parser.add_argument("url", help="URL of a large HTTP(S) file")
    args = parser.parse_args()

    try:
        parsed_url = urllib.parse.urlsplit(args.url)
        _ = parsed_url.port
        valid_url = (
            parsed_url.scheme in {"http", "https"}
            and bool(parsed_url.hostname)
        )
    except ValueError:
        valid_url = False

    if not valid_url:
        parser.error("a valid HTTP(S) URL is required")

    total_bytes = 0
    total_seconds = 0.0

    try:
        for request_number in range(1, REQUEST_COUNT + 1):
            downloaded, elapsed = download(args.url)
            total_bytes += downloaded
            total_seconds += elapsed
            print(
                f"Request {request_number:2}: "
                f"{elapsed:.3f} s, {downloaded / 1_000_000:.2f} MB"
            )
    except (OSError, ValueError) as error:
        print(f"Download error: {error}", file=sys.stderr)
        return 1

    print(f"\nAverage request time: {total_seconds / REQUEST_COUNT:.3f} s")
    print(f"Downloaded data: {total_bytes / 1_000_000:.2f} MB")
    speed = calculate_speed(total_bytes, total_seconds)
    print(f"Average speed: {speed:.2f} MB/s ({speed * 8:.2f} Mbit/s)")

    return 0


if __name__ == "__main__":
    self_test()
    sys.exit(main())
