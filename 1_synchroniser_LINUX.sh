#!/bin/bash

# Sync with remote data

set -ex

workdir=$(dirname "$0")

(
# subshell so we do not need to care about restoring CWD
cd "$workdir"

git pull

)  # subshell
