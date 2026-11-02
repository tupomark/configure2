"""Conservative static checks reflecting the teacher's quality rules."""

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ("src", "tests", "scripts")
SNAKE = re.compile(r"^_?[a-z][a-z0-9_]*_$|^_?[a-z][a-z0-9_]*$")
MAX_LINE = 80
MAX_FUNCTION = 40
MAX_ARGS = 7
MAX_COMPLEXITY = 10
MAX_FILE_LINES = 1000


def decisions(function):
    """Estimate McCabe complexity from decisions in a function body."""
    total = 1
    branches = (ast.If, ast.For, ast.AsyncFor, ast.While,
                ast.ExceptHandler, ast.IfExp, ast.Assert)
    for node in ast.walk(function):
        if node is function:
            continue
        if isinstance(node, branches):
            total += 1
        if isinstance(node, ast.BoolOp):
            total += len(node.values) - 1
        if isinstance(node, ast.comprehension):
            total += 1 + len(node.ifs)
    return total


def inspect_function(node, file):
    """Return violations of naming, size, complexity and docs."""
    failures = []
    name = node.name
    if not (SNAKE.fullmatch(name) or (
            name.startswith("__") and name.endswith("__"))):
        failures.append(f"{file}:{node.lineno}: invalid name {name}")
    length = node.end_lineno - node.lineno + 1
    if length > MAX_FUNCTION:
        failures.append(f"{file}:{node.lineno}: function {length} lines")
    args = node.args
    total_args = len(args.posonlyargs) + len(args.args) + len(args.kwonlyargs)
    if total_args > MAX_ARGS:
        failures.append(f"{file}:{node.lineno}: {total_args} arguments")
    complexity = decisions(node)
    if complexity > MAX_COMPLEXITY:
        failures.append(f"{file}:{node.lineno}: complexity {complexity}")
    if not ast.get_docstring(node):
        failures.append(f"{file}:{node.lineno}: missing docstring")
    return failures


def inspect_file(file):
    """Check file and source limits for every Python unit."""
    failures = []
    content = file.read_text(encoding="utf-8")
    lines = content.splitlines()
    if len(lines) > MAX_FILE_LINES:
        failures.append(f"{file}: file exceeds 1000 lines")
    for index, line in enumerate(lines, 1):
        if len(line) > MAX_LINE:
            failures.append(f"{file}:{index}: over 80 characters")
    tree = ast.parse(content, filename=str(file))
    if not ast.get_docstring(tree):
        failures.append(f"{file}: missing module docstring")
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            failures.extend(inspect_function(node, file))
    return failures


def main():
    """Print every quality violation and return a nonzero exit code."""
    files = [file for folder in SOURCES
             for file in (ROOT / folder).rglob("*.py")]
    failures = []
    for file in sorted(files):
        failures.extend(inspect_file(file))
    for failure in failures:
        print(failure)
    if failures:
        return 1
    print(f"PASS: quality checks ({len(files)} Python files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
