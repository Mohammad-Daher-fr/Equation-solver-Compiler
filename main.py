import argparse
import sys
import os
import urllib.parse
import urllib.request
import tempfile

from Equation_Solver import Compiler


def fetch_source(source: str) -> str:
    """
    Fetch the content of `source`, which can be a local path or an HTTP/HTTPS URL.
    Returns the file contents as a string or exits on error.
    """
    parsed = urllib.parse.urlparse(source)
    if parsed.scheme in ("http", "https"):
        try:
            with urllib.request.urlopen(source) as resp:
                return resp.read().decode()
        except Exception as e:
            print(f"Error fetching URL {source}: {e}")
            sys.exit(1)
    else:
        if not os.path.exists(source):
            print(f"File not found: {source}")
            sys.exit(1)
        try:
            with open(source, "r") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {source}: {e}")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Solve a system of equations from a text file or URL"
    )
    parser.add_argument(
        "source",
        help="Local path or URL of the equations file (e.g. equations.txt or https://...)",
    )
    args = parser.parse_args()

    data = fetch_source(args.source)

    # Write to a temporary file so Compiler.compile can read it
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".txt") as tmp:
        tmp.write(data)
        tmp_path = tmp.name

    compiler = Compiler()
    compiler.compile(tmp_path)


if __name__ == "__main__":
    main()
