"""Produce D2 graph descriptions and render them into PNG files."""

import shutil
import subprocess
from pathlib import Path


def d2_label(text):
    """Escape double quotation marks and backslashes in D2 labels."""
    return text.replace("\\", "\\\\").replace('"', '\\"')


def to_d2(graph):
    """Render all graph nodes and directed edges as valid D2 text."""
    nodes = sorted(graph.edges)
    identifiers = {node: f"node_{index}" for index, node in enumerate(nodes)}
    lines = ["direction: right"]
    for node in nodes:
        label = d2_label(f"{node[0]} {node[1]}")
        lines.append(f'{identifiers[node]}: "{label}"')
    for parent in nodes:
        for child in sorted(graph.edges[parent]):
            lines.append(f"{identifiers[parent]} -> {identifiers[child]}")
    return "\n".join(lines) + "\n"


def render_graph(graph, output, d2_executable=None):
    """Save D2 source and use a D2 CLI executable to create PNG."""
    target = Path(output)
    if target.suffix.lower() != ".png":
        raise ValueError("Output must be a PNG file")
    target.parent.mkdir(parents=True, exist_ok=True)
    source = target.with_suffix(".d2")
    source.write_text(to_d2(graph), encoding="utf-8")
    executable = d2_executable or shutil.which("d2")
    if not executable:
        raise RuntimeError("D2 CLI is required; D2 source was saved")
    result = subprocess.run([executable, str(source), str(target)],
                            text=True, capture_output=True, check=False)
    if result.returncode:
        raise RuntimeError(f"D2 renderer failed: {result.stderr.strip()}")
    if not target.is_file() or target.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError("Renderer did not produce a valid PNG header")
    return source, target
