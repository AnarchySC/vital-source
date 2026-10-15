#!/usr/bin/env bash
# Drive the real drill CLI through every lesson to mastery inside the image.
#   tests/smoke.sh            (from the repo root, image already built)
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
VOL=learn-linux-smoke
docker volume rm -f "$VOL" >/dev/null

# Interactive bash so ~/.bashrc (and its drill wrapper) loads, as for a learner.
gen() {
    echo "drill start 0"
    for lesson in 0 1 2; do
        for _ in $(seq 60); do
            echo 'eval "$(python3 /tmp/tests/smoke_solver.py)" >/dev/null'
        done
        echo "drill stats"
        echo "drill start $((lesson + 1)) 2>/dev/null || true"
    done
    echo "drill list"
}

gen | docker run --rm -i -v "$VOL:/var/lib/drill" -v "$ROOT/drill/tests:/tmp/tests:ro" \
    -v "$ROOT/drill/drill:/tmp/drill:ro" anarchygames/learn-linux:dev bash -i 2>&1 \
    | sed 's/\x1b\[[0-9;]*m//g' | grep -v '^learner@sandbox' | grep -vE 'job control|process group'

echo "--- progress survives a fresh container:"
docker run --rm -v "$VOL:/var/lib/drill" anarchygames/learn-linux:dev bash -lc 'drill list' 2>&1 \
    | sed 's/\x1b\[[0-9;]*m//g' | grep -E '^\s+\S\s+[0-9]'
docker volume rm -f "$VOL" >/dev/null
