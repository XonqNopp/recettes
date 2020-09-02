#!/bin/sh

# Save the current state.
# Commit to git and push.
git commit -am "Snapshot of `date +%Y-%m-%dT%H:%M`"
# TODO configure user and email as well as username and credentials

# Build PDF and HTML.
sphinx-build -b latex . _build/latex
latexpawa _build/latex/Recettes.tex

sphinx-build -b html . _build/html

# Upload to website.
rsync -r _build/html x@y:xonqnopp.ch/recettes

