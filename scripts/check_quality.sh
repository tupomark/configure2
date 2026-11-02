#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python3 -m compileall -q src tests scripts
python3 -m scripts.quality
git diff --check
