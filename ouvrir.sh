#!/bin/sh
formats="html latex"

for format in $formats; do
	sphinx-build -W -b "$format" . "_build/$format" || exit 1
done

cd _build/latex && latexpawa Recettes.tex

