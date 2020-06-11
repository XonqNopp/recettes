#!/bin/bash

# View the current state.


# Build sphinx with our settings
# Args:
# 1: builder (latex, html)
function sphinxBuild() {
	sphinx-build -W -b "$1" . "_build/$1" || exit 1
}


workdir=$(dirname "$0")

(
# subshell so we do not need to care about restoring CWD
cd "$workdir" || exit -1

pdfFilename="_build/latex/Recettes.pdf"
rm -f "$pdfFilename"
touch "$pdfFilename"


if command -v latex > /dev/null; then
	# LaTeX PDF
	sphinxBuild "latex"
	rm -f "$pdfFilename"
	python scripts/fix_latex.py || exit 1

	(
		# subshell to not have to come back to previous dir after
		cd _build/latex || exit 1
		latexpawa Recettes.tex || exit 1
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

if [ "$(uname)" = "Linux" ]; then
	firefox _build/html/index.html
else
	open _build/html/index.html
fi

)  # subshell

