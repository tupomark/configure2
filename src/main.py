"""Entry point for the staged NuGet graph application."""

import json
import sys
from urllib.error import HTTPError, URLError
from xml.etree.ElementTree import ParseError

from .config import (
    STAGE_CONFIG, STAGE_NUGET, STAGE_GRAPH, STAGE_REVERSE,
    STAGE_RENDER, parse_arguments,
)
from .nuget import NugetRepository


def run_stage2(args):
    """Display directly declared dependencies of a NuGet package."""
    repo = NugetRepository(args.repository, args.framework)
    for package, requirement in repo.dependencies(args.package, args.version):
        print(f"{package} {requirement}")
    return 0


def main(argv=None):
    """Select the available stages and return a meaningful exit status."""
    args = parse_arguments(argv)
    if args.stage == STAGE_CONFIG:
        for key, value in vars(args).items():
            print(f"{key}={value}")
        return 0
    try:
        if args.stage == STAGE_NUGET:
            return run_stage2(args)
        print("This stage is not implemented yet", file=sys.stderr)
        return 1
    except (OSError, ValueError, KeyError, ParseError,
            HTTPError, URLError, json.JSONDecodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
