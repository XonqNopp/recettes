#!/bin/bash

set -ex

workdir=$(dirname "$0")

(
# subshell so we do not need to care about restoring CWD
cd "$workdir"

PYTHON=python3
if [ -e "./_venv/bin/python" ]; then
    PYTHON="./_venv/bin/python"
fi

# Create and open a new file with an easy text editor.
filename=$($PYTHON scripts/app.py)

if [ "$filename" != "" ]; then
    # Commit new file.
    git commit -m "New: $filename"
fi

)  # subshell
