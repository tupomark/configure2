"""Read NuGet V3 PackageBaseAddress without third-party libraries."""

import json
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from .versions import normalize, select_version

HTTP_TIMEOUT = 15
MAX_RESPONSE = 10 * 1024 * 1024


def fetch_bytes(url):
    """Retrieve a bounded NuGet resource with a request timeout."""
    request = Request(url, headers={"User-Agent": "pr2-v31/1.0"})
    with urlopen(request, timeout=HTTP_TIMEOUT) as response:
        result = response.read(MAX_RESPONSE + 1)
    if len(result) > MAX_RESPONSE:
        raise ValueError("NuGet response is larger than 10 MiB")
    return result


def local_name(tag):
    """Remove the default XML namespace from an element name."""
    return tag.rsplit("}", 1)[-1]


def children(element, name):
    """Find direct XML children without requiring a namespace prefix."""
    return [item for item in element if local_name(item.tag) == name]


def select_groups(groups, framework):
    """Resolve an optional exact target framework within .nuspec."""
    if not framework:
        return groups
    selected = [item for item in groups if (
        item.get("targetFramework", "").casefold() == framework.casefold()
    )]
    if groups and not selected:
        raise ValueError(f"Target framework {framework} not found")
    return selected


def parse_nuspec(data, framework=None):
    """Extract direct dependencies from metadata and selected groups."""
    root = ElementTree.fromstring(data)
    metadata = next((item for item in root.iter()
                     if local_name(item.tag) == "metadata"), None)
    if metadata is None:
        raise ValueError("NuGet package has no metadata")
    containers = children(metadata, "dependencies")
    if not containers:
        return []
    container = containers[0]
    groups = select_groups(children(container, "group"), framework)
    elements = children(container, "dependency")
    for group in groups:
        elements.extend(children(group, "dependency"))
    result = set()
    for item in elements:
        identifier = item.get("id")
        if not identifier:
            raise ValueError("Dependency has no id")
        result.add((identifier, item.get("version", "*")))
    return sorted(result, key=lambda item: (item[0].casefold(), item[1]))


def package_base(index):
    """Find NuGet V3 PackageBaseAddress resource in service index."""
    for item in index.get("resources", []):
        kinds = item.get("@type", "")
        kinds = [kinds] if isinstance(kinds, str) else kinds
        if any(str(kind).startswith("PackageBaseAddress/")
               for kind in kinds):
            return item["@id"].rstrip("/")
    raise ValueError("NuGet index has no PackageBaseAddress")


class NugetRepository:
    """Cache available versions and declared dependencies during a run."""

    def __init__(self, index_url, framework=None, fetcher=fetch_bytes):
        """Load the NuGet V3 service index and determine the flat feed."""
        self.fetcher = fetcher
        self.framework = framework
        self.base = package_base(json.loads(fetcher(index_url)))
        self.version_cache = {}
        self.dependency_cache = {}

    def versions(self, name):
        """Return all published versions from the flat container."""
        key = name.casefold()
        if key not in self.version_cache:
            url = f"{self.base}/{key}/index.json"
            self.version_cache[key] = json.loads(self.fetcher(url))["versions"]
        return self.version_cache[key]

    def resolve(self, name, requirement):
        """Choose a compatible version under NuGet range constraints."""
        return select_version(self.versions(name), requirement)

    def dependencies(self, name, version):
        """Read the declared direct dependencies of an exact package."""
        package = name.casefold()
        normalized = normalize(version)
        key = package, normalized
        if key not in self.dependency_cache:
            url = f"{self.base}/{package}/{normalized}/{package}.nuspec"
            self.dependency_cache[key] = parse_nuspec(
                self.fetcher(url), self.framework
            )
        return self.dependency_cache[key]
