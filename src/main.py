"""Entry point for the staged NuGet graph application."""

from .config import (
    STAGE_CONFIG, STAGE_NUGET, STAGE_GRAPH, STAGE_REVERSE,
    STAGE_RENDER, parse_arguments,
)


def main(argv=None):
    """Show the requested configuration in the first assignment stage."""
    args = parse_arguments(argv)
    if args.stage != STAGE_CONFIG:
        print("This stage is not implemented yet")
        return 1
    for key, value in vars(args).items():
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
