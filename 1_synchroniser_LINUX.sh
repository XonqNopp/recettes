#!/bin/bash

# Sync with remote data

workdir=$(dirname "$0")

(
# subshell so we do not need to care about restoring CWD
cd "$workdir" || exit -1

git pull

)  # subshell

