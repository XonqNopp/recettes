#!/bin/bash

# Save the current state.

set -ex


# Fail and warn about it
function fail() {
    echo
    echo
    echo "********** ATTENTION **********"
    echo
    echo "Probleme lors de la synchronisation avec le serveur! 60s pour lire les erreurs..."
    echo
    sleep 60
    exit 1
}


workdir=$(dirname "$0")

(
# subshell so we do not need to care about restoring CWD
cd "$workdir"

# Commit to git and push.
git add .  # just to be sure in case some files moved
git commit -am "Snapshot of $(date +%Y-%m-%dT%H:%M)" # no fail, we want at least to pull
git pull || fail
git push || fail
# TODO configure user and email as well as username and credentials

# Upload to website.
#rsync -r _build/html x@y:xonqnopp.ch/recettes  # TODO

)  # subshell
