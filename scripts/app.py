#!/usr/bin/env python3
"""
This script opens a GUI app to introduce a new recipe.
"""
# pylint: disable=[logging-fstring-interpolation]
from pathlib import Path
import sys
import re
from argparse import ArgumentParser
import logging
from subprocess import run
from enum import Enum
from typing import TypedDict

# pylint: disable=[import-error]
from PySide6 import QtWidgets  # type: ignore


class Categories(Enum):
    """
    Enum for categories.
    """
    UTILISATION = 0
    CUISINE = 1
    COSMETIQUE = 2

    UNDEFINED = None


DEFAULT_CATEGORY = Categories.CUISINE


class Templates(Enum):
    """
    Enum for templates.
    """
    AUCUN = 0
    STANDARD = 1
    # All values >=2 are for "X personnes" template
    PERSONNES2 = 2
    PERSONNES4 = 4

    UNDEFINED = None


DEFAULT_TEMPLATE = Templates.STANDARD


class ResultsDict(TypedDict):
    """ Type hints for results dict. """
    category: Categories
    title: str
    template: Templates
    exit_code: int
    basename: str
    filename: Path


def get_basename(title: str) -> str:
    """
    Get the basename for the new recipe WITHOUT the prefixed dirname.
    """
    title = title.strip()

    logging.debug(f'Prepare basename for title={title}')

    # Format filename
    translate_table: dict[int, int | str | None] = {}

    translate_table.update(
        str.maketrans(
            'áàâäãçéêèëẽíìîïĩóòôöõúùûüũýỳŷÿỹñÁÀÂÄÃÉÈÊËẼÍÌÎÏĨÓÒÔÖÕÚÙÛÜŨÝỲŶŸỸÑ',
            'aaaaaceeeeeiiiiiooooouuuuuyyyyynAAAAAEEEEEIIIIIOOOOOUUUUUYYYYYN'
        )
    )

    translate_table[ord('æ')] = 'ae'
    translate_table[ord('œ')] = 'oe'

    translate_table[ord('Æ')] = 'AE'
    translate_table[ord('Œ')] = 'OE'

    title = title.translate(translate_table)

    title = title.lower()  # no .title because ordering messed if upper and lowercase letters mixed
    # snake_case:
    title = title.replace(' ', '_')
    title = title.replace('-', '_')
    title = title.replace("'", '_')
    title = title.replace('"', '')
    title = title.replace(',', '')
    title = title.replace('(', '')
    title = title.replace(')', '')
    title = title.replace('[', '')
    title = title.replace(']', '')
    title = title.replace('{', '')
    title = title.replace('}', '')

    # Get rid of non-standard characters
    title = re.sub(r'()\[\]{}"\/:;.,?!<>+&%=$°§ßµ', '', title)

    logging.debug(f'title formatted: {title}')

    return title + '.rst'


def get_filename(basename: str, category: Categories) -> Path:
    """
    Get the filename for the new recipe.

    Args:
        basename (str)
        category (Categories)

    Returns:
        (Path) filename
    """
    return Path(category.name.lower()) / basename


class Recettes(QtWidgets.QDialog):
    """
    Pop-up window to create a new recette in this repo.
    """
    BUTTON_STATUS = {
        0: False,  # cancel
        1: True,  # ok
    }

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._logger = logging.getLogger(self.__class__.__name__)

        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(self.categories())
        layout.addWidget(self.title())
        layout.addWidget(self.templates())
        layout.addWidget(self.buttons())

        self.setLayout(layout)

        self.setWindowTitle('Ajouter une nouvelle recette')

    def categories(self) -> QtWidgets.QGroupBox:
        """
        Sets the categories as radio buttons.
        """
        self._logger.debug('Setting categories widget')

        layout = QtWidgets.QVBoxLayout()

        self._categories: dict[Categories, QtWidgets.QRadioButton] = {}

        for category in Categories:
            if category is Categories.UNDEFINED:
                continue

            self._categories[category] = QtWidgets.QRadioButton(category.name.lower())

        self._categories[DEFAULT_CATEGORY].setChecked(True)

        for category in Categories:
            if category is Categories.UNDEFINED:
                continue

            layout.addWidget(self._categories[category])

        categories = QtWidgets.QGroupBox('Catégorie')
        categories.setLayout(layout)

        return categories

    def get_category(self) -> Categories:
        """
        Read which category is selected.
        """
        for category in Categories:
            if category is Categories.UNDEFINED:
                continue

            is_checked = self._categories[category].isChecked()
            self._logger.debug(f'category {category.name} is checked: {is_checked}')

            if is_checked:
                return category

        return Categories.UNDEFINED

    def title(self) -> QtWidgets.QGroupBox:
        """
        Sets the title as text input field.
        """
        self._logger.debug('Setting title widget')

        self._title = QtWidgets.QLineEdit()
        self._title.setFixedWidth(500)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self._title)

        title = QtWidgets.QGroupBox('Titre')
        title.setLayout(layout)

        return title

    def get_title(self) -> str:
        """
        Read the title field contents.
        """
        title = self._title.text()
        self._logger.debug(f'title={title}')
        return title

    def templates(self) -> QtWidgets.QGroupBox:
        """
        Sets the template as radio buttons.
        """
        self._logger.debug('Setting templates widget')

        layout = QtWidgets.QVBoxLayout()

        templates = QtWidgets.QGroupBox('Modèle')

        self._templates: dict[Templates, QtWidgets.QRadioButton] = {}

        for template in Templates:
            if template is Templates.UNDEFINED:
                continue

            self._templates[template] = QtWidgets.QRadioButton(template.name.lower())

        self._templates[DEFAULT_TEMPLATE].setChecked(True)

        for template in Templates:
            if template is Templates.UNDEFINED:
                continue

            layout.addWidget(self._templates[template])

        templates.setLayout(layout)

        return templates

    def get_template(self) -> Templates:
        """
        Read which template is selected.
        """
        for template in Templates:
            if template is Templates.UNDEFINED:
                continue

            is_checked = self._templates[template].isChecked()

            self._logger.debug(f'template {template.name} is checked: {is_checked}')

            if is_checked:
                return template

        return Templates.UNDEFINED

    def is_title_empty(self) -> bool:
        """
        Check if title is empty.
        """
        empty_title = bool(self.get_title() == '')
        self._logger.debug(f'title is empty={empty_title}')
        return empty_title

    def reject_empty_title(self) -> None:
        """
        Reject if title is empty.
        """
        self._logger.debug('REJECTED: empty title not allowed')

        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowTitle('Titre manquant')
        msg_box.setText('Le titre ne peut pas etre vide')
        msg_box.exec()

    def confirm_use_existing_file(self, filename: Path) -> bool:
        """
        Ask user if existing file is the one to use.

        Returns:
            False if user does not want to use existing one.
        """
        self._logger.debug(f'File {filename} exists, ask user confirmation to use it')

        msg_box = QtWidgets.QMessageBox()

        msg_box.setWindowTitle(f'{filename} existe...')
        msg_box.setText(f'Le fichier {filename} existe déjà. Est-ce bien celui que tu veux éditer?')

        msg_box.setStandardButtons(msg_box.Yes | msg_box.No)
        msg_box.setDefaultButton(msg_box.No)

        msg_box.exec()

        return msg_box.result() == msg_box.Yes

    def accept(self) -> None:
        """
        What to do when user clicks on OK.
        """
        self._logger.debug('accept')

        if self.is_title_empty():
            self.reject_empty_title()
            return

        filename = get_filename(get_basename(self.get_title()), self.get_category())
        if filename.exists() and not self.confirm_use_existing_file(filename):
            return

        super().accept()

    def buttons(self) -> QtWidgets.QDialogButtonBox:
        """
        Buttons for the app.
        """
        self._logger.debug('Setting buttons widget')

        self._buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok
            | QtWidgets.QDialogButtonBox.Cancel
        )

        self._buttons.accepted.connect(self.accept)
        self._buttons.rejected.connect(self.reject)

        return self._buttons

    def get_button(self) -> bool:
        """
        Read which button was clicked.
        """
        button_status = self.BUTTON_STATUS[self.result()]
        self._logger.debug(f'Clicked on OK={button_status}')
        return button_status

    def get_inputs(self) -> dict:
        """
        Get all the user inputs we need to run post-processing.
        """
        return {
            'button': self.get_button(),
            'category': self.get_category(),
            'title': self.get_title(),
            'template': self.get_template(),
        }


class App:
    """
    Main app handling post-processing too.
    """
    NEWLINE = '\n'

    def __init__(self, title, category, template) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)

        self._title = title
        self._category = category
        self._template = template

        self._results: ResultsDict | None = None

    @property
    def exit_code(self) -> int:
        """
        Get the exit code.
        """
        if self._results is None:
            # Not defined yet
            return 0

        return self._results['exit_code']

    def run_gui(self) -> dict:
        """
        Run the GUI app (no post-processing here).
        """
        app = QtWidgets.QApplication(sys.argv)
        recettes = Recettes()
        recettes.show()
        exit_code = app.exec_()

        results = recettes.get_inputs()
        results['exit_code'] = exit_code

        if exit_code == 0 and not results['button']:
            exit_code = 1

        if exit_code != 0:
            sys.exit(exit_code)

        return results

    def run(self) -> None:
        """
        Run the GUI app if needed.
        """
        results = {
            'category': self._category,
            'title': self._title,
            'template': self._template,
            'exit_code': 0,
        }

        if self._title is None:
            results = self.run_gui()

        basename = get_basename(results['title'])

        self._results = {
            'category': results['category'],
            'title': results['title'],
            'template': results['template'],
            'exit_code': results['exit_code'],
            'basename': basename,
            'filename': get_filename(basename, results['category']),

        }

        self._logger.debug(self._results)

    def _create_default_file(self) -> None:
        """
        Create a default file with the template if applicable.
        """
        if self._results is None:
            raise ValueError('Cannot create file before parsing results')

        contents = ''

        template_filename = Path(__file__).parent / 'template.rst'
        if self._results['template'] is not Templates.AUCUN or not template_filename.exists():
            self._logger.debug(f'Reading template: {template_filename}')

            contents = template_filename.read_text(encoding='utf-8')

        if self._results['template'].value >= 2:
            self._logger.debug(f'Using template for {self._results["template"]}')
            n_people = self._results['template'].value

            table_line = (
                '+------------+-------------+---------------------------------------------------+'
            )

            contents = contents.replace(
                '* eau',
                f"""{table_line}
| 1 personne | {n_people} personnes |                                                   |
{table_line.replace('-', '=')}
|          1 |           A | eau                                               |
{table_line}""",
            )

        index_string = self._results['title']

        if self._results['category'] is not Categories.CUISINE:
            index_string = f'{self._results["category"].name.lower()}; {index_string}'

        new_contents = f'.. index:: {index_string}\n'

        new_contents += (
            '.. _'
            + self._results['category'].name.lower()
            + '_'
            + self._results['basename'].replace('.rst', '')
            + ':\n'
        )

        new_contents += '\n'
        new_contents += self._results['title'] + '\n'
        new_contents += '#' * len(self._results['title']) + '\n'
        new_contents += contents

        self._results['filename'].write_text(new_contents)

    def _create_utilisation_file(self) -> None:
        """
        Create a file for utilisation category.
        """
        if self._results is None:
            raise ValueError('Cannot create file before parsing results')

        contents = f'.. index:: {self._results["title"]}\n'
        contents += f'.. _{self._results["title"]}:\n'
        contents += '\n'
        contents += self._results['title'] + '\n'
        contents += '#' * len(self._results['title']) + '\n'
        contents += '\n'

        self._results['filename'].write_text(contents)

    def create_file(self) -> None:
        """
        Create file from template (except if file exists).
        """
        if self._results is None:
            raise ValueError('Cannot create file before parsing results')

        if self._results['filename'].exists():
            self._logger.debug(
                f'File {self._results["filename"]} already exists, skipping creation from template'
            )
            return

        if self._results['category'] is Categories.UTILISATION:
            self._create_utilisation_file()

            print('WARNING: you must manually edit utilisation/index.rst '
                  f'to add the new file {self._results["filename"]}')

        else:
            self._create_default_file()

    def git_stage_file(self) -> None:
        """
        Stage touched files to git for the next commit.
        """
        if self._results is None:
            raise ValueError('Cannot stage file before parsing results')

        command = ['git', 'add', str(self._results['filename'])]
        self._logger.debug(' '.join(command))
        run(command, check=True)

    def confirm(self) -> None:
        """
        Confirm file is ready.
        """
        if self._results is None:
            raise ValueError('Cannot prepare before parsing results')

        if self._results['title'] is None:
            msg_box = QtWidgets.QMessageBox()
            msg_box.setWindowTitle('Nouvelle recette prête')

            msg_box.setText(
                'La nouvelle recette peut maintenant être éditée dans:\n'
                + f'{self._results["filename"]}'
            )

            msg_box.exec()

        print(self._results['filename'])

    def process(self) -> int:
        """
        Run the complete post-processing.
        """
        self.create_file()
        self.git_stage_file()

        self.confirm()

        return self.exit_code


def main() -> int:
    """
    Main function.
    """
    # Parser
    parser = ArgumentParser()

    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        default=False,
    )

    parser.add_argument(
        '-t',
        '--title',
        help='Titre de la recette'
    )

    parser.add_argument(
        '-c',
        '--category',
        choices=[category.name.lower() for category in Categories if category.name != 'UNDEFINED'],
        default=DEFAULT_CATEGORY.name.lower(),
        help=f'Categorie de la recette (defaut={DEFAULT_CATEGORY.name.lower()})'
    )

    parser.add_argument(
        '--template',
        choices=[template.name for template in Templates if template.name != 'UNDEFINED'],
        default=DEFAULT_TEMPLATE.name,
        help=f'Modele pour demarrer la recette (defaut={DEFAULT_TEMPLATE.name})'
    )

    args = parser.parse_args()

    # Logging
    log_format = '%(asctime)s:%(levelname)s:%(funcName)s[%(lineno)d]:%(message)s'
    if args.verbose:
        logging.basicConfig(format=log_format, level=logging.DEBUG)
    else:
        logging.basicConfig(format=log_format, level=logging.INFO)

    # App
    app = App(args.title, Categories[args.category.upper()], Templates[args.template])
    app.run()
    exit_code = app.process()

    return exit_code


if __name__ == '__main__':
    sys.exit(main())
