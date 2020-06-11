#!/bin/bash

workdir=$(dirname "$0")

(
# subshell so we do not need to care about restoring CWD
cd "$workdir" || exit -1

# Create and open a new file with an easy text editor.
filename=$(python3 scripts/app.py)
if [ "$filename" != "" ]; then

	# Commit new file.
	git commit -m "New: $filename"

fi

)  # subshell

