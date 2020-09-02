#!/bin/sh

# Create and open a new file with an easy text editor.
filename=`python scripts/app.py`

# Commit new file.
git commit -m "New: $filename"

