#!/bin/sh

# View the current state.

# LaTeX PDF
sphinx-build -W -b "latex" . "_build/latex" || exit 1
python scripts/fix_latex.py || exit 1
cd _build/latex && latexpawa Recettes.tex || exit 1

# HTML
sphinx-build -W -b "html" . "_build/html" || exit 1

