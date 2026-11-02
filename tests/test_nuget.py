"""Stage-two NuGet XML, version ranges, fetcher and error tests."""

import json
import unittest

from src.nuget import NugetRepository, parse_nuspec
from src.versions import normalize, select_version, version_key

XML = b'''<package xmlns="urn:nuget"><metadata><dependencies>
<group targetFramework="net8.0"><dependency id="B" version="[1,2)"/>
</group><group targetFramework="net9.0"/>
</dependencies></metadata></package>'''


class NugetTests(unittest.TestCase):
    """Exercise NuGet parsing without relying on public network access."""

    def test_xml_groups(self):
        """Distinguish a missing framework from an existing empty group."""
        self.assertEqual(parse_nuspec(XML), [("B", "[1,2)")])
        self.assertEqual(parse_nuspec(XML, "net9.0"), [])
        with self.assertRaises(ValueError):
            parse_nuspec(XML, "net7.0")
        with self.assertRaises(ValueError):
            parse_nuspec(b"<package/>")

    def test_ranges(self):
        """Include exact and floating ranges and prerelease precedence."""
        versions = ["1.0.0", "1.5.0", "2.0.0", "3.0.0-beta.1"]
        cases = {
            "[1.0,2.0)": "1.0.0",
            "(1.0,2.0]": "1.5.0",
            "[2.0.0]": "2.0.0",
            "1.4": "1.5.0",
            "1.*": "1.5.0",
            "*": "1.0.0",
        }
        for requirement, expected in cases.items():
            with self.subTest(requirement=requirement):
                actual = select_version(versions, requirement)
                self.assertEqual(actual, expected)
        self.assertLess(
            version_key("1.0.0-beta.2"), version_key("1.0.0-beta.10")
        )
        self.assertEqual(normalize("01.02.003.0+build"), "1.2.3")
        with self.assertRaises(ValueError):
            select_version(versions, "[4.0.0]")

    def test_repository_fetch_and_cache(self):
        """Request the NuGet index, versions and one .nuspec only once."""
        calls = []
        prefix = "https://example.test/flat"
        mapping = {
            "https://example.test/v3/index.json": json.dumps({
                "resources": [{"@type": "PackageBaseAddress/3.0.0",
                               "@id": prefix}]
            }).encode(),
            f"{prefix}/a/index.json": b'{"versions":["1.0.0"]}',
            f"{prefix}/a/1.0.0/a.nuspec": XML,
        }

        def fetch(url):
            """Use deterministic in-memory responses for NuGet calls."""
            calls.append(url)
            return mapping[url]

        repo = NugetRepository("https://example.test/v3/index.json",
                               fetcher=fetch)
        self.assertEqual(repo.resolve("A", "1.0.0"), "1.0.0")
        self.assertEqual(repo.resolve("A", "1.0.0"), "1.0.0")
        self.assertEqual(repo.dependencies("A", "1"), [("B", "[1,2)")])
        self.assertEqual(repo.dependencies("A", "1.0.0"), [("B", "[1,2)")])
        self.assertEqual(len(calls), 3)
