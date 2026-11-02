"""Offline end-to-end demonstration of the NuGet stage-two CLI."""

import subprocess
import sys

from scripts.local_feed import local_feed


def run_case(url, package, version, expected):
    """Validate exact dependency output from a real local HTTP feed."""
    command = [sys.executable, "-m", "src.main", "--package", package,
               "--version", version, "--repository", url, "--stage", "2"]
    result = subprocess.run(command, text=True, capture_output=True,
                            check=False)
    if result.returncode or result.stdout.strip() != expected:
        raise AssertionError(f"Bad stage-two output: {result}")


def main():
    """Demonstrate distinct versions and no transitive output."""
    with local_feed() as url:
        run_case(url, "A", "1.0.0", "B [1.0.0,2.0.0)")
        run_case(url, "A", "2.0.0", "C 1.0.0")
        run_case(url, "C", "1.0.0", "")
    print("PASS: stage 2")


if __name__ == "__main__":
    main()
