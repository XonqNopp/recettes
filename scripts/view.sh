#!/bin/sh

# View the current state.
sphinx-build -W -b "latex" . "_build/latex" || exit 1
cd _build/latex && latexpawa Recettes.tex || exit 1

sphinx-build -W -b "html" . "_build/html" || exit 1

