#!/bin/bash

# View the current state.


PYTHON=python3
SPHINX="sphinx-build"
if [ -e "./_venv/bin/python" ]; then
    PYTHON="./_venv/bin/python"
    SPHINX="./_venv/bin/sphinx-build"
fi


# Build sphinx with our settings
# Args:
# 1: builder (latex, html)
function sphinxBuild() {
    $SPHINX -W -b "$1" . "_build/$1" || exit 1
}


workdir=$(dirname "$0")

(
# subshell so we do not need to care about restoring CWD
cd "$workdir" || exit 1


# Generate index
$PYTHON scripts/generate_index.py cuisine cosmetique


# LaTeX
pdfFilename="_build/latex/Recettes.pdf"
rm -f "$pdfFilename"
touch "$pdfFilename"

if command -v latex > /dev/null; then
    # LaTeX PDF
    sphinxBuild "latex"
    rm -f "$pdfFilename"
    $PYTHON scripts/fix_latex.py || exit 1

    (
        # subshell to not have to come back to previous dir after
        cd _build/latex || exit 1
        latexpawa.pl Recettes.tex || exit 1
    )  # subshell

else
    echo
    echo
    echo "********** ATTENTION **********"
    echo
    echo "L'outil PDF n'est pas installe sur cet ordinateur, seulement la version web sera preparee dans 5s"
    echo
    sleep 5
fi


# HTML
sphinxBuild "html"

)  # subshell
