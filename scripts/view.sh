#!/bin/sh

# View the current state.

rm -f _build/latex/Recettes.pdf
touch _build/latex/Recettes.pdf

# LaTeX PDF
sphinx-build -W -b "latex" . "_build/latex" || exit 1
rm -f _build/latex/Recettes.pdf
python scripts/fix_latex.py || exit 1
cd _build/latex && latexpawa Recettes.tex || exit 1

# HTML
sphinx-build -W -b "html" . "_build/html" || exit 1

