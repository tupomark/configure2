"""Read a deterministic JSON NuGet-style repository for testing."""

import json
from pathlib import Path

from .versions import normalize, select_version

PACKAGE_NAME_LENGTH = 1
EDGE_FIELDS = 2


class TestRepository:
    """Validate and query packages with single-letter uppercase names."""

    __test__ = False

    def __init__(self, filename):
        """Load package -> version -> list of (dependency, range) pairs."""
        self.data = json.loads(Path(filename).read_text(encoding="utf-8"))
        if not isinstance(self.data, dict) or not self.data:
            raise ValueError("Repository must be a nonempty JSON object")
        for package, versions in self.data.items():
            self._validate_package(package, versions)

    def _validate_package(self, package, versions):
        """Check the shape of a package and each declared version."""
        if len(package) != PACKAGE_NAME_LENGTH or not ("A" <= package <= "Z"):
            raise ValueError("Test package names must be uppercase A-Z")
        if not isinstance(versions, dict):
            raise ValueError("Test package versions must be an object")
        for version, dependencies in versions.items():
            self._validate_version(version, dependencies)

    def _validate_version(self, version, dependencies):
        """Validate a version and all its outgoing dependencies."""
        normalize(version)
        if not isinstance(dependencies, list):
            raise ValueError("Dependencies must be a list")
        for edge in dependencies:
            self._validate_edge(edge)

    def _validate_edge(self, edge):
        """Check one JSON edge with package name and range."""
        if not isinstance(edge, list) or len(edge) != EDGE_FIELDS:
            raise ValueError("An edge must have name and range")
        if not all(isinstance(value, str) for value in edge):
            raise ValueError("Edge values must be strings")
        if len(edge[0]) != PACKAGE_NAME_LENGTH or not ("A" <= edge[0] <= "Z"):
            raise ValueError("Invalid test dependency name")

    def versions(self, package):
        """Return all available versions of a fixture package."""
        if package not in self.data:
            raise KeyError(f"Missing test package {package}")
        return sorted(self.data[package])

    def resolve(self, package, requirement):
        """Choose a version satisfying the requested NuGet-style range."""
        return select_version(self.versions(package), requirement)

    def dependencies(self, package, version):
        """Return the direct fixture dependencies for an exact version."""
        if package not in self.data:
            raise KeyError(f"Missing test package {package}")
        for declared, dependencies in self.data[package].items():
            if normalize(declared) == normalize(version):
                return [tuple(item) for item in dependencies]
        raise KeyError(f"Unknown version {version} of {package}")
