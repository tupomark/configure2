#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
command -v d2 >/dev/null || { echo 'Missing D2 CLI' >&2; exit 1; }
command -v dotnet >/dev/null || { echo 'Missing dotnet SDK' >&2; exit 1; }
python3 -m scripts.demonstrate
