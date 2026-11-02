"""Compare three real NuGet graphs with independent .NET SDK output."""

import json
import subprocess
import tempfile
from pathlib import Path

from src.graph import GraphBuilder
from src.nuget import NugetRepository
from src.visualize import render_graph

INDEX = "https://api.nuget.org/v3/index.json"
PACKAGES = (
    ("Serilog.Sinks.Console", "6.0.0"),
    ("Serilog.Sinks.File", "6.0.0"),
    ("Serilog.Formatting.Compact", "3.0.0"),
)


def command(args, folder):
    """Execute a .NET SDK command and report any unsuccessful result."""
    result = subprocess.run(args, cwd=folder, text=True,
                            capture_output=True, check=False)
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout)
    return result.stdout


def native_graph(package, version):
    """Independently use dotnet restore and list its exact package set."""
    with tempfile.TemporaryDirectory() as folder:
        command(["dotnet", "new", "classlib", "--framework", "net8.0",
                 "--no-restore"], folder)
        command(["dotnet", "add", "package", package, "--version",
                 version], folder)
        output = command(["dotnet", "list", "package",
                          "--include-transitive", "--format", "json"],
                         folder)
        result = json.loads(output)
    packages = set()
    for project in result.get("projects", []):
        for framework in project.get("frameworks", []):
            groups = ("topLevelPackages", "transitivePackages")
            for group in groups:
                for item in framework.get(group, []):
                    packages.add((item["id"].lower(),
                                  item["resolvedVersion"].lower()))
    return packages


def compare(graph, native):
    """Report exact package/version overlap and both differences."""
    actual = {(name.lower(), version.lower()) for name, version in graph.edges}
    return {
        "matches": actual == native,
        "only_custom": sorted(actual - native),
        "only_dotnet": sorted(native - actual),
    }


def main():
    """Create real D2/PNG examples and machine-readable .NET comparisons."""
    results = {}
    output = Path("output/real")
    for name, version in PACKAGES:
        repo = NugetRepository(INDEX)
        graph = GraphBuilder(repo, 10).build(name, version)
        render_graph(graph, output / f"{name}.png")
        results[name] = compare(graph, native_graph(name, version))
    output.mkdir(parents=True, exist_ok=True)
    (output / "comparison.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
