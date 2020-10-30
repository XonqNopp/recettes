#!/bin/bash

# View the current state.

rm -f _build/latex/Recettes.pdf
touch _build/latex/Recettes.pdf

# LaTeX PDF
sphinx-build -W -b "latex" . "_build/latex" || exit 1
rm -f _build/latex/Recettes.pdf
python scripts/fix_latex.py || exit 1

(
# subshell to not have to come back to previous dir after
cd _build/latex || exit 1
latexpawa Recettes.tex || exit 1
)

# HTML
sphinx-build -W -b "html" . "_build/html" || exit 1

