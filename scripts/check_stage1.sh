#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python3 -m unittest tests.test_config -v
./run.sh --package Example --version 1.0.0 --stage 1 | grep -q 'package=Example'
if ./run.sh --package 'bad name' --version 1 2>/dev/null; then
    echo 'Invalid package was accepted' >&2
    exit 1
fi
echo 'PASS: stage 1'
