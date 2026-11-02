"""Command-line configuration and argument validation."""

import argparse
import re
from pathlib import Path
from urllib.parse import urlsplit

DEFAULT_INDEX = "https://api.nuget.org/v3/index.json"
PACKAGE_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*\Z")
VERSION_PATTERN = re.compile(
    r"[0-9]+(?:\.[0-9]+){0,3}"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-.]+)?\Z"
)
MAX_DEPTH = 100
MIN_DEPTH = 0
STAGE_CONFIG = 1
STAGE_NUGET = 2
STAGE_GRAPH = 3
STAGE_REVERSE = 4
STAGE_RENDER = 5


def package_id(value):
    """Require an ordinary NuGet package identifier."""
    if not PACKAGE_PATTERN.fullmatch(value):
        raise argparse.ArgumentTypeError("Invalid package identifier")
    return value


def package_version(value):
    """Require a specific NuGet version, not a version range."""
    if not VERSION_PATTERN.fullmatch(value):
        raise argparse.ArgumentTypeError("Invalid package version")
    return value


def depth(value):
    """Restrict recursion depth to an explicit finite range."""
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Depth must be an integer") from exc
    if not MIN_DEPTH <= number <= MAX_DEPTH:
        raise argparse.ArgumentTypeError("Depth must be between 0 and 100")
    return number


def nonempty(value):
    """Reject empty or whitespace-only filter values."""
    if not value.strip():
        raise argparse.ArgumentTypeError("Filter cannot be empty")
    return value


def image_path(value):
    """Require a PNG path that represents a file rather than a folder."""
    path = Path(value)
    if path.suffix.lower() != ".png" or not path.name:
        raise argparse.ArgumentTypeError("Output must be a PNG file")
    return str(path)


def create_parser():
    """Describe all stage-one settings and the stage selector."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", required=True, type=package_id)
    parser.add_argument("--version", required=True, type=package_version)
    parser.add_argument("--repository", default=DEFAULT_INDEX)
    parser.add_argument("--test-repo", action="store_true")
    parser.add_argument("--output", default="output/graph.png", type=image_path)
    parser.add_argument("--max-depth", default=3, type=depth)
    parser.add_argument("--exclude", type=nonempty)
    parser.add_argument("--framework")
    parser.add_argument("--reverse", type=package_id)
    parser.add_argument("--stage", type=int, choices=range(1, 6), default=1)
    return parser


def validate_source(parser, args):
    """Allow a local JSON test source or an HTTP(S) NuGet index."""
    if args.test_repo:
        if not args.repository.endswith(".json"):
            parser.error("Test repository must be a JSON file")
        if not Path(args.repository).is_file():
            parser.error("Test repository file does not exist")
        return
    url = urlsplit(args.repository)
    if url.scheme not in ("http", "https") or not url.netloc:
        parser.error("Repository must be an HTTP(S) URL")


def parse_arguments(argv=None):
    """Parse command-line arguments and report input errors as exit 2."""
    parser = create_parser()
    args = parser.parse_args(argv)
    validate_source(parser, args)
    if args.test_repo and not re.fullmatch(r"[A-Z]", args.package):
        parser.error("Test packages must use one uppercase Latin letter")
    if args.test_repo and args.reverse:
        if not re.fullmatch(r"[A-Z]", args.reverse):
            parser.error("Reversed test package must be an uppercase letter")
    return args
