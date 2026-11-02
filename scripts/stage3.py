"""End-to-end stage-three CLI validation on multiple fixture graphs."""

import subprocess
import sys


def graph_output(fixture, depth, excluded=None):
    """Exercise the actual command-line application using local JSON."""
    command = [sys.executable, "-m", "src.main", "--package", "A",
               "--version", "1", "--test-repo", "--repository", fixture,
               "--max-depth", str(depth), "--stage", "3"]
    if excluded:
        command.extend(["--exclude", excluded])
    return subprocess.run(command, capture_output=True, text=True,
                          check=False)


def main():
    """Assert cycle preservation, depth limits and case-folded filter."""
    cycle = graph_output("examples/cycle.json", 5)
    assert not cycle.returncode, cycle.stderr
    assert "EDGE C 1.0.0 -> A 1.0.0" in cycle.stdout
    shallow = graph_output("examples/cycle.json", 0)
    assert not shallow.returncode, shallow.stderr
    assert "EDGE" not in shallow.stdout
    filtered = graph_output("examples/cycle.json", 5, "b")
    assert not filtered.returncode, filtered.stderr
    assert "EDGE" not in filtered.stdout
    diamond = graph_output("examples/diamond.json", 3)
    assert not diamond.returncode, diamond.stderr
    assert "EDGE D 1.0.0 -> E 1.0.0" in diamond.stdout
    print("PASS: stage 3")


if __name__ == "__main__":
    main()
