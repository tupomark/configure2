"""Automated tests for CLI configuration and invalid input."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from src.config import parse_arguments
from src.main import main


class ConfigTests(unittest.TestCase):
    """Keep stage-one functionality independently testable."""

    def test_valid_options(self):
        """Print every user-configurable parameter in key=value form."""
        args = ["--package", "Serilog", "--version", "4.0.0"]
        with contextlib.redirect_stdout(io.StringIO()) as stream:
            status = main(args)
        self.assertEqual(status, 0)
        self.assertIn("package=Serilog", stream.getvalue())
        self.assertIn("version=4.0.0", stream.getvalue())
        self.assertIn("max_depth=3", stream.getvalue())
        self.assertIn("test_repo=False", stream.getvalue())
        self.assertIn("output=output/graph.png", stream.getvalue())

    def test_invalid_settings(self):
        """Reject invalid package, version, depth, filter and output."""
        base = ["--package", "A", "--version", "1.0.0"]
        cases = [
            ["--package", "bad name"],
            ["--version", "[1,2)"],
            ["--max-depth", "-1"],
            ["--max-depth", "101"],
            ["--max-depth", "abc"],
            ["--exclude", "  "],
            ["--output", "graph.svg"],
            ["--repository", "file:///tmp/repo"],
            ["--stage", "7"],
        ]
        for option in cases:
            with self.subTest(option=option):
                argv = base + option
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit) as error:
                        parse_arguments(argv)
                self.assertEqual(error.exception.code, 2)

    def test_test_repository_validation(self):
        """Only allow an existing JSON file with A-Z package names."""
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "repository.json"
            target.write_text("{}", encoding="utf-8")
            args = ["--package", "A", "--version", "1.0.0"]
            args += ["--test-repo", "--repository", str(target)]
            self.assertTrue(parse_arguments(args).test_repo)
            args[1] = "Package"
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    parse_arguments(args)

    def test_required_settings(self):
        """Package and version must be supplied explicitly."""
        for args in (["--version", "1"], ["--package", "A"]):
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    parse_arguments(args)
            self.assertEqual(error.exception.code, 2)
