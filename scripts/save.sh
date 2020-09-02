#!/bin/sh

# Save the current state.
# Commit to git and push.
git commit -am "Snapshot of `date +%Y-%m-%dT%H:%M`" || exit 1
git pull || exit 1
git push || exit 1
# TODO configure user and email as well as username and credentials

# Build PDF and HTML.
./scripts/view.sh || exit 1

# Upload to website.
rsync -r _build/html x@y:xonqnopp.ch/recettes  # TODO || exit 1

