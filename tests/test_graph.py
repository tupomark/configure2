"""Stage-three DFS, depth, cycle and filter tests."""

import unittest

from src.graph import GraphBuilder, graph_lines
from src.test_repository import TestRepository

CYCLE = "examples/cycle.json"
DIAMOND = "examples/diamond.json"


class GraphTests(unittest.TestCase):
    """Verify recursive traversal semantics and test JSON fixtures."""

    def test_cycle_terminates_and_keeps_edge(self):
        """Preserve cycle closure while avoiding infinite traversal."""
        repo = TestRepository(CYCLE)
        graph = GraphBuilder(repo, 5).build("A", "1")
        self.assertIn(("A", "1.0.0"), graph.edges[("C", "1.0.0")])
        self.assertEqual(len(graph.edges), 4)

    def test_depth_zero_and_one(self):
        """Keep boundary nodes but do not expand them."""
        repo = TestRepository(CYCLE)
        zero = GraphBuilder(repo, 0).build("A", "1")
        one = GraphBuilder(repo, 1).build("A", "1")
        self.assertEqual(len(zero.edges), 1)
        self.assertEqual(zero.edges[("A", "1.0.0")], [])
        self.assertEqual(len(one.edges), 2)
        self.assertEqual(one.edges[("B", "1.0.0")], [])

    def test_filter_excludes_transitive_package(self):
        """Skip a filtered package and its outgoing traversal."""
        repo = TestRepository(CYCLE)
        graph = GraphBuilder(repo, 5, "b").build("A", "1")
        self.assertEqual(len(graph.edges), 1)
        with self.assertRaises(ValueError):
            GraphBuilder(repo, 5, "a").build("A", "1")

    def test_shorter_diamond_path(self):
        """Revisit a shared node found first via a deeper DFS route."""
        repo = TestRepository(DIAMOND)
        graph = GraphBuilder(repo, 3).build("A", "1")
        self.assertIn(("E", "1.0.0"), graph.edges[("D", "1.0.0")])
        self.assertEqual(len(graph.edges), 6)
        self.assertTrue(graph_lines(graph)[0].startswith("ROOT A"))

    def test_invalid_test_source(self):
        """Reject broken JSON formats and unknown fixture versions."""
        repo = TestRepository(CYCLE)
        with self.assertRaises(KeyError):
            repo.dependencies("Z", "1.0.0")
        with self.assertRaises(ValueError):
            repo.resolve("A", "[2.0.0]")
