"""Stage-four tests for incoming direct and transitive consumers."""

import unittest

from src.graph import GraphBuilder
from src.reverse import reverse_graph, build_test_universe
from src.test_repository import TestRepository


class ReverseTests(unittest.TestCase):
    """Verify reverse DFS on the complete local test universe."""

    def test_incoming_consumers(self):
        """Show A and D as direct consumers of B, C as transitive."""
        original = build_test_universe(TestRepository("examples/cycle.json"))
        graph = reverse_graph(original, "B", 3)
        self.assertIn(("A", "1.0.0"), graph.edges[("B", "1.0.0")])
        self.assertIn(("D", "1.0.0"), graph.edges[("B", "1.0.0")])
        self.assertIn(("C", "1.0.0"), graph.edges[("A", "1.0.0")])

    def test_no_consumers(self):
        """Return only E when no test package depends on E."""
        graph = build_test_universe(TestRepository("examples/cycle.json"))
        reversed_graph = reverse_graph(graph, "E", 3)
        self.assertEqual(len(reversed_graph.edges), 1)
        self.assertEqual(reversed_graph.edges[("E", "1.0.0")], [])

    def test_reverse_depth_and_filter(self):
        """Honor stage-three depth and exclusion while reversing edges."""
        graph = build_test_universe(TestRepository("examples/cycle.json"))
        shallow = reverse_graph(graph, "B", 1)
        self.assertEqual(shallow.edges[("A", "1.0.0")], [])
        excluded = reverse_graph(graph, "B", 3, "d")
        self.assertNotIn(("D", "1.0.0"), excluded.edges)

    def test_reverse_only_reachable_real_scope(self):
        """Reverse a graph in the same scope as the earlier forward DFS."""
        repo = TestRepository("examples/cycle.json")
        forward = GraphBuilder(repo, 1).build("A", "1")
        backward = reverse_graph(forward, "B", 3)
        self.assertEqual(backward.edges[("B", "1.0.0")],
                         [("A", "1.0.0")])
        with self.assertRaises(ValueError):
            reverse_graph(forward, "E", 3)
