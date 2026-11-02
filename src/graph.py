"""Recursive depth-limited DFS dependency graph implementation."""

from dataclasses import dataclass, field

from .versions import normalize


@dataclass
class Graph:
    """Directed graph whose vertices are exact (package, version) pairs."""

    root: tuple
    edges: dict = field(default_factory=dict)

    def add(self, node, neighbors):
        """Add new edges without removing already observed cycle edges."""
        current = self.edges.setdefault(node, [])
        for neighbor in neighbors:
            if neighbor not in current:
                current.append(neighbor)
        for neighbor in neighbors:
            self.edges.setdefault(neighbor, [])


class GraphBuilder:
    """Visit each node at its lowest known depth and preserve cycles."""

    def __init__(self, repository, max_depth, exclude=None):
        """Store repository and traversal constraints."""
        self.repository = repository
        self.max_depth = max_depth
        self.exclude = (exclude or "").casefold()
        self.best_depth = {}
        self.graph = None

    def _excluded(self, name):
        """Check a case-insensitive substring filter."""
        return bool(self.exclude and self.exclude in name.casefold())

    def build(self, package, version):
        """Build a graph by recursive DFS from an exact root version."""
        if self._excluded(package):
            raise ValueError("Root package is excluded by filter")
        root = package, normalize(version)
        self.graph = Graph(root)
        self.best_depth = {}
        self._visit(root, 0)
        return self.graph

    def _visit(self, node, depth):
        """Revisit shared nodes only if a shorter path is found."""
        if depth >= self.best_depth.get(node, self.max_depth + 1):
            return
        self.best_depth[node] = depth
        self.graph.edges.setdefault(node, [])
        if depth >= self.max_depth:
            return
        neighbors = []
        for package, requirement in self.repository.dependencies(*node):
            if self._excluded(package):
                continue
            version = self.repository.resolve(package, requirement)
            neighbors.append((package, version))
        neighbors.sort(key=lambda item: (item[0].casefold(), item[1]))
        self.graph.add(node, neighbors)
        for child in neighbors:
            self._visit(child, depth + 1)


def graph_lines(graph):
    """Return deterministic lines listing directed dependency edges."""
    lines = [f"ROOT {graph.root[0]} {graph.root[1]}"]
    for parent in sorted(graph.edges):
        targets = sorted(graph.edges[parent])
        if not targets:
            lines.append(f"NODE {parent[0]} {parent[1]}")
        for child in targets:
            lines.append(
                f"EDGE {parent[0]} {parent[1]} -> {child[0]} {child[1]}"
            )
    return lines
