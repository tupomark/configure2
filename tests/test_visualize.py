"""Stage-five D2 source and PNG renderer integration tests."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.graph import GraphBuilder
from src.test_repository import TestRepository
from src.visualize import render_graph, to_d2


class VisualizeTests(unittest.TestCase):
    """Require D2 source and a verifiable PNG output file."""

    def test_d2_edges_and_nodes(self):
        """Produce deterministic node identifiers and cycle edges."""
        repo = TestRepository("examples/cycle.json")
        graph = GraphBuilder(repo, 3).build("A", "1")
        source = to_d2(graph)
        self.assertIn('node_0: "A 1.0.0"', source)
        self.assertIn('node_0 -> node_1', source)
        self.assertIn('node_2 -> node_0', source)
        self.assertEqual(source, to_d2(graph))

    def test_missing_renderer_retains_source(self):
        """Never pretend that a PNG exists without a renderer."""
        repo = TestRepository("examples/cycle.json")
        graph = GraphBuilder(repo, 2).build("A", "1")
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "graph.png"
            with patch("src.visualize.shutil.which", return_value=None):
                with self.assertRaises(RuntimeError):
                    render_graph(graph, str(target))
            self.assertTrue(target.with_suffix(".d2").exists())
            self.assertFalse(target.exists())

    def test_executable_called_for_png(self):
        """Ensure the renderer receives source and image output paths."""
        repo = TestRepository("examples/cycle.json")
        graph = GraphBuilder(repo, 2).build("A", "1")
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "graph.png"
            fake = Path(folder) / "d2"
            fake.write_text(
                "#!/bin/sh\nprintf '\\211PNG\\r\\n\\032\\n' > \"$2\"\n",
                encoding="utf-8",
            )
            fake.chmod(0o755)
            source, image = render_graph(graph, target, str(fake))
            self.assertTrue(source.exists())
            self.assertEqual(image.read_bytes()[:4], b"\x89PNG")
