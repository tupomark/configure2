#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
for stage in 1 2 3 4 5; do
    "./scripts/check_stage${stage}.sh"
done
