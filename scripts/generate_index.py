#!/usr/bin/env python3
"""
Generate the index.rst in the subdirectories.
"""
from argparse import ArgumentParser
from pathlib import Path


INDENT = '   '
INDEX_FILENAME = 'index.rst'
IGNORED_FILES = [
    INDEX_FILENAME,
    '.gitignore',
]


def generate_index(directory: str | Path):
    """
    Generate index.rst file for a subdirectory.

    Args:
        directory (str|Path): subdirectory to go through
    """
    print(f'Generating index.rst for {directory}...')

    title = str(directory)
    directory = Path(directory)

    index = directory / INDEX_FILENAME

    contents = ''
    contents += title.capitalize() + '\n'
    contents += '#' * len(title) + '\n'
    contents += '\n'
    contents += '.. toctree::\n'
    contents += f'{INDENT}:maxdepth: 1\n'
    contents += '\n'

    for file in sorted(directory.iterdir()):
        filename = file.name

        if filename in IGNORED_FILES:
            continue

        contents += f'{INDENT}{filename}\n'

    index.write_text(contents)


def main():
    """ Main function called when executing this file. """
    parser = ArgumentParser()

    parser.add_argument(
        dest='directories',
        nargs='+',
        help='Directories to generate index to',
    )

    args = parser.parse_args()

    for directory in args.directories:
        generate_index(directory)


if __name__ == '__main__':
    main()
