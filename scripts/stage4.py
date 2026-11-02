"""Run the stage-four backward dependency checks through the CLI."""

import subprocess
import sys


def run_case(package, depth=3, excluded=None):
    """Run reverse DFS on the local cyclic fixture graph."""
    argv = [sys.executable, "-m", "src.main", "--package", package,
            "--version", "1.0.0", "--test-repo", "--stage", "4",
            "--repository", "examples/cycle.json", "--max-depth",
            str(depth)]
    if excluded:
        argv.extend(["--exclude", excluded])
    return subprocess.run(argv, text=True, capture_output=True,
                          check=False)


def main():
    """Check incoming consumers, empty incoming graph, and filtering."""
    result = run_case("B")
    assert result.returncode == 0, result.stderr
    assert "EDGE B 1.0.0 -> A 1.0.0" in result.stdout
    assert "EDGE B 1.0.0 -> D 1.0.0" in result.stdout
    assert "EDGE A 1.0.0 -> C 1.0.0" in result.stdout
    empty = run_case("E")
    assert empty.returncode == 0, empty.stderr
    assert "EDGE" not in empty.stdout
    filtered = run_case("B", excluded="d")
    assert filtered.returncode == 0, filtered.stderr
    assert "EDGE B 1.0.0 -> D" not in filtered.stdout
    print("PASS: stage 4")


if __name__ == "__main__":
    main()
