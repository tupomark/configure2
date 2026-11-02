"""Entry point for the staged NuGet graph application."""

import json
import sys
from urllib.error import HTTPError, URLError
from xml.etree.ElementTree import ParseError

from .config import (
    STAGE_CONFIG, STAGE_NUGET, STAGE_GRAPH, STAGE_REVERSE,
    STAGE_RENDER, parse_arguments,
)
from .graph import GraphBuilder, graph_lines
from .reverse import reverse_graph, build_test_universe
from .test_repository import TestRepository
from .visualize import render_graph
from .nuget import NugetRepository


def run_stage2(args):
    """Display directly declared dependencies of a NuGet package."""
    repo = NugetRepository(args.repository, args.framework)
    for package, requirement in repo.dependencies(args.package, args.version):
        print(f"{package} {requirement}")
    return 0


def run_stage3(args):
    """Construct the recursive dependency graph and print its edges."""
    if args.test_repo:
        repo = TestRepository(args.repository)
    else:
        repo = NugetRepository(args.repository, args.framework)
    graph = GraphBuilder(repo, args.max_depth, args.exclude).build(
        args.package, args.version
    )
    print("\n".join(graph_lines(graph)))
    return 0


def run_stage4(args):
    """List incoming dependencies in the selected graph universe."""
    if args.test_repo:
        graph = build_test_universe(TestRepository(args.repository))
    else:
        repo = NugetRepository(args.repository, args.framework)
        graph = GraphBuilder(repo, args.max_depth, args.exclude).build(
            args.package, args.version
        )
    target = args.reverse or args.package
    reversed_graph = reverse_graph(
        graph, target, args.max_depth, args.exclude
    )
    print("\n".join(graph_lines(reversed_graph)))
    return 0


def run_stage5(args):
    """Save a D2 dependency description and corresponding PNG image."""
    if args.test_repo:
        repo = TestRepository(args.repository)
    else:
        repo = NugetRepository(args.repository, args.framework)
    graph = GraphBuilder(repo, args.max_depth, args.exclude).build(
        args.package, args.version
    )
    if args.reverse:
        graph = reverse_graph(graph, args.reverse, args.max_depth,
                              args.exclude)
    source, image = render_graph(graph, args.output)
    print(f"D2: {source}")
    print(f"PNG: {image}")
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
        if args.stage == STAGE_GRAPH:
            return run_stage3(args)
        if args.stage == STAGE_REVERSE:
            return run_stage4(args)
        if args.stage == STAGE_RENDER:
            return run_stage5(args)
        print("This stage is not implemented yet", file=sys.stderr)
        return 1
    except (OSError, RuntimeError, ValueError, KeyError, ParseError,
            HTTPError, URLError, json.JSONDecodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
