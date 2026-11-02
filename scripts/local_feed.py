"""Temporary local NuGet V3 HTTP service for offline CLI tests."""

import contextlib
import json
import shutil
import tempfile
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

FEED_ROOT = Path(__file__).resolve().parent.parent / "examples/nuget/flat"


@contextlib.contextmanager
def local_feed():
    """Serve the flat container and a dynamic service index on localhost."""
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        shutil.copytree(FEED_ROOT, root / "flat")
        handler = partial(SimpleHTTPRequestHandler, directory=folder)
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        address = f"http://127.0.0.1:{server.server_address[1]}"
        index = {"resources": [
            {"@type": "PackageBaseAddress/3.0.0", "@id": address + "/flat"}
        ]}
        (root / "v3").mkdir()
        (root / "v3/index.json").write_text(json.dumps(index),
                                             encoding="utf-8")
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            yield address + "/v3/index.json"
        finally:
            server.shutdown()
            worker.join()
            server.server_close()
