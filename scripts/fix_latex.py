#!/usr/bin/env python3
"""
Fix _build/latex/Recettes.tex before typesetting.

* usepackage[table]{xcolor} BEFORE usepackage{sphinx}
* rowcolors at each begin{tabulary}
"""
import os.path
import re

def main():
    """
    Main function.
    """
    filename = os.path.join('_build', 'latex', 'Recettes.tex')

    print('{}: post-processing...'.format(filename))

    # Read
    #with open(filename, 'r', encoding='utf-8') as texFile:
    with open(filename, 'r') as texFile:
        contents = texFile.read()

    # Alternate table row colors
    contents = re.sub('\\\\usepackage{sphinx}', '\\\\usepackage[table]{xcolor}\n\\\\usepackage{sphinx}', contents)
    contents = re.sub('\\\\centering\n\\\\begin{tabulary}', '\\\\rowcolors{1}{gray!20}{}\n\\\\begin{tabulary}', contents)

    # Remove unwanted font
    contents = re.sub('\\\\sphinxstyletheadfamily', '\\\\bfseries', contents)

    # Write back
    with open(filename, 'w') as texFile:
        texFile.write('% Pimped by python\n')
        texFile.write(contents)

if __name__ == "__main__":
    main()

