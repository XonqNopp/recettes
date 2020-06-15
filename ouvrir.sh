#!/bin/sh

# Build PDF first so we can provide it as download in html
sphinx-build -W -b "latex" . "_build/latex" || exit 1
cd _build/latex && latexpawa Recettes.tex || exit 1

sphinx-build -W -b "html" . "_build/html" || exit 1

