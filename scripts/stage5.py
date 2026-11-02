"""Offline CLI integration check using a controlled renderer fixture."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path


def run_demo(folder, package, renderer):
    """Invoke the actual fifth-stage CLI and check generated files."""
    output = Path(folder) / f"{package}.png"
    command = [sys.executable, "-m", "src.main", "--package", package,
               "--version", "1", "--test-repo", "--stage", "5",
               "--repository", "examples/cycle.json", "--output",
               str(output)]
    env = dict(os.environ)
    env["PATH"] = f"{renderer}:{env.get('PATH', '')}"
    result = subprocess.run(command, capture_output=True, text=True,
                            check=False, env=env)
    assert not result.returncode, result.stderr
    assert output.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
    assert output.with_suffix(".d2").exists()


def main():
    """Check the D2 renderer interface for packages A, B and E."""
    with tempfile.TemporaryDirectory() as folder:
        fake = Path(folder) / "d2"
        fake.write_text(
            "#!/bin/sh\nprintf '\\211PNG\\r\\n\\032\\n' > \"$2\"\n",
            encoding="utf-8",
        )
        fake.chmod(0o755)
        for package in ("A", "B", "E"):
            run_demo(folder, package, folder)
    print("PASS: stage 5 (renderer interface simulated)")


if __name__ == "__main__":
    main()
