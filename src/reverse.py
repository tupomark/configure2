"""Reverse NuGet graph traversal using the stage-three recursive DFS."""

from .graph import Graph, GraphBuilder
from .versions import normalize, select_version


def build_test_universe(repository):
    """Collect every package version and direct edge in a local fixture."""
    first = sorted(repository.data)[0]
    graph = Graph((first, normalize(repository.versions(first)[0])))
    for name in sorted(repository.data):
        for version in repository.versions(name):
            targets = []
            for package, requirement in repository.dependencies(name, version):
                selected = repository.resolve(package, requirement)
                targets.append((package, selected))
            graph.add((name, normalize(version)), sorted(targets))
    return graph


def merge_graphs(graphs):
    """Combine reverse walks of several exact versions of one package."""
    if not graphs:
        raise ValueError("No matching packages in graph")
    merged = Graph(graphs[0].root)
    for graph in graphs:
        for parent, neighbors in graph.edges.items():
            merged.add(parent, neighbors)
    return merged


class ReversedRepository:
    """Adapt a directed graph to the stage-three traversal interface."""

    def __init__(self, graph):
        """Index incoming edges, preserving the exact consumer version."""
        self.parents = {node: [] for node in graph.edges}
        for parent, targets in graph.edges.items():
            for target in targets:
                self.parents.setdefault(target, []).append(parent)
        for parent in self.parents:
            self.parents[parent].sort()

    def versions(self, package):
        """List versions of the selected graph package."""
        return [version for name, version in self.parents if name == package]

    def resolve(self, package, requirement):
        """Select the exact consumer version from the reversed graph."""
        return select_version(self.versions(package), requirement)

    def dependencies(self, package, version):
        """List incoming consumer edges as exact NuGet-style ranges."""
        parents = self.parents.get((package, normalize(version)), [])
        return [(name, f"[{found}]") for name, found in parents]


def reverse_graph(graph, target, max_depth, exclude=None):
    """Follow all consumers of a package using the same recursive DFS."""
    repo = ReversedRepository(graph)
    versions = sorted(set(repo.versions(target)))
    if not versions:
        raise ValueError(f"Package {target} is not in the selected graph")
    graphs = [
        GraphBuilder(repo, max_depth, exclude).build(target, version)
        for version in versions
    ]
    return merge_graphs(graphs)
