#!/usr/bin/env python3
# coding=utf-8
"""
This script opens a GUI app to introduce a new recipe.
"""
from pathlib import Path
import sys
import re
from collections import OrderedDict
from argparse import ArgumentParser
import logging
from subprocess import run
from enum import Enum
from PySide2 import QtWidgets


class Categories(Enum):
    """
    Enum for categories.
    """
    utilisation = 0
    cuisine = 1
    cosmetique = 2

    UNDEFINED = None


DEFAULT_CATEGORY = Categories.cuisine


class Templates(Enum):
    """
    Enum for templates.
    """
    aucun = 0
    standard = 1
    # All values >=2 are for "X personnes" template
    personnes2 = 2
    personnes3 = 3
    personnes4 = 4
    personnes5 = 5
    personnes6 = 6
    personnes7 = 7
    personnes8 = 8

    UNDEFINED = None


DEFAULT_TEMPLATE = Templates.standard


def get_basename(title: str) -> str:
    """
    Get the basename for the new recipe WITHOUT the prefixed dirname.
    """
    title = title.strip()

    logging.debug(f'Prepare basename for title={title}')

    # Format filename
    translateTable = str.maketrans(
        'áàâäãçéêèëẽíìîïĩóòôöõúùûüũýỳŷÿỹñÁÀÂÄÃÉÈÊËẼÍÌÎÏĨÓÒÔÖÕÚÙÛÜŨÝỲŶŸỸÑ',
        'aaaaaceeeeeiiiiiooooouuuuuyyyyynAAAAAEEEEEIIIIIOOOOOUUUUUYYYYYN'
    )

    translateTable[ord('æ')] = 'ae'
    translateTable[ord('œ')] = 'oe'

    translateTable[ord('Æ')] = 'AE'
    translateTable[ord('Œ')] = 'OE'

    title = title.translate(translateTable)

    title = title.lower()  # no .title because ordering is then messed if there are upper and lowercase letters mixed
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


def getFilename(basename: str, category: Categories) -> str:
    """
    Get the filename for the new recipe.

    Args:
        basename (str)
        category (Categories)

    Returns:
        (Path) filename
    """
    return Path(category.name) / basename


class Recettes(QtWidgets.QDialog):
    """
    Pop-up window to create a new recette in this repo.
    """
    BUTTON_STATUS = {
        0: False,  # cancel
        1: True,  # ok
    }

    def __init__(self, parent=None):
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

        self._categories = {}

        for category in Categories:
            if category.name == 'UNDEFINED':
                continue

            self._categories[category] = QtWidgets.QRadioButton(category.name)

        self._categories[DEFAULT_CATEGORY].setChecked(True)

        for category in Categories:
            if category.name == 'UNDEFINED':
                continue

            layout.addWidget(self._categories[category])

        categories = QtWidgets.QGroupBox('Catégorie')
        categories.setLayout(layout)

        return categories

    def getCategory(self) -> str:
        """
        Read which category is selected.
        """
        logString = 'categories:'
        for category in Categories:
            if category.name == 'UNDEFINED':
                continue

            logString += f' {category.name}={self._categories[category].isChecked()}'

        self._logger.debug(logString)

        for category in Categories:
            if category.name == 'UNDEFINED':
                continue

            if self._categories[category].isChecked():
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

    def getTitle(self) -> str:
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

        self._templates = {}
        for template in Templates:
            if template.name == 'UNDEFINED':
                continue

            self._templates[template] = QtWidgets.QRadioButton(template.name)

        self._templates[DEFAULT_TEMPLATE].setChecked(True)

        for template in Templates:
            if template.name == 'UNDEFINED':
                continue

            layout.addWidget(self._templates[template])

        templates.setLayout(layout)

        return templates

    def getTemplate(self) -> str:
        """
        Read which template is selected.
        """
        logString = 'templates:'
        for template in Templates:
            if template.name == 'UNDEFINED':
                continue

            logString += f' {template.name}={self._templates[template].isChecked()}'

        self._logger.debug(logString)

        for template in Templates:
            if template.name == 'UNDEFINED':
                continue

            if self._templates[template].isChecked():
                return template

        return Templates.UNDEFINED

    def isTitleEmpty(self) -> bool:
        """
        Check if title is empty.
        """
        emptyTitle = bool(self.getTitle() == '')
        self._logger.debug(f'title is empty={emptyTitle}')
        return emptyTitle

    def rejectEmptyTitle(self) -> None:
        """
        Reject if title is empty.
        """
        self._logger.debug('REJECTED: empty title not allowed')

        msgBox = QtWidgets.QMessageBox()
        msgBox.setWindowTitle('Titre manquant')
        msgBox.setText('Le titre ne peut pas etre vide')
        msgBox.exec()

    def confirmUseExistingFile(self, filename: Path) -> bool:
        """
        Ask user if existing file is the one to use.

        Returns:
            False if user does not want to use existing one.
        """
        self._logger.debug(f'File {filename} exists, ask user confirmation to use it')

        msgBox = QtWidgets.QMessageBox()

        msgBox.setWindowTitle(f'{filename} existe...')
        msgBox.setText(f'Le fichier {filename} existe déjà. Est-ce bien celui que tu veux éditer?')

        msgBox.setStandardButtons(msgBox.Yes | msgBox.No)
        msgBox.setDefaultButton(msgBox.No)

        msgBox.exec()

        return msgBox.result() == msgBox.Yes

    def accept(self) -> None:
        """
        What to do when user clicks on OK.
        """
        self._logger.debug('accept')

        if self.isTitleEmpty():
            self.rejectEmptyTitle()
            return

        filename = getFilename(get_basename(self.getTitle()), self.getCategory())
        if filename.exists and not self.confirmUseExistingFile(filename):
            return

        super().accept()

    def buttons(self) -> QtWidgets.QDialogButtonBox:
        """
        Buttons for the app.
        """
        self._logger.debug('Setting buttons widget')

        self._buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self._buttons.accepted.connect(self.accept)
        self._buttons.rejected.connect(self.reject)

        return self._buttons

    def getButton(self) -> bool:
        """
        Read which button was clicked.
        """
        buttonStatus = self.BUTTON_STATUS[self.result()]
        self._logger.debug(f'Clicked on OK={buttonStatus}')
        return buttonStatus

    def getInputs(self) -> OrderedDict:
        """
        Get all the user inputs we need to run post-processing.
        """
        return OrderedDict([
            ('button', self.getButton()),
            ('category', self.getCategory()),
            ('title', self.getTitle()),
            ('template', self.getTemplate()),
        ])


class App:
    """
    Main app handling post-processing too.
    """
    NEWLINE = '\n'

    def __init__(self, title, category, template):
        self._logger = logging.getLogger(self.__class__.__name__)

        self._title = title
        self._category = category
        self._template = template

        self._results = None

    @property
    def exitCode(self):
        """
        Get the exit code.
        """
        if self._results is None:
            # Not defined yet
            return 0

        return self._results['exitCode']

    def runGUI(self):
        """
        Run the GUI app (no post-processing here).
        """
        app = QtWidgets.QApplication(sys.argv)
        recettes = Recettes()
        recettes.show()
        exitCode = app.exec_()

        self._results = recettes.getInputs()
        if exitCode == 0 and not self._results['button']:
            exitCode = 1

        if exitCode != 0:
            sys.exit(exitCode)

        self._results['exitCode'] = exitCode

    def run(self):
        """
        Run the GUI app if needed.
        """
        if self._title is None:
            self.runGUI()

        else:
            # store results
            self._results = OrderedDict()
            self._results['category'] = self._category
            self._results['title'] = self._title
            self._results['template'] = self._template
            self._results['exitCode'] = 0

        self._results['basename'] = get_basename(self._results['title'])
        self._results['filename'] = getFilename(self._results['basename'], self._results['category'])

        self._logger.debug(self._results)

    def _createDefaultFile(self):
        """
        Create a default file with the template if applicable.
        """
        contents = ''

        templateFilename = Path(__file__).parent / 'template.rst'
        if self._results['template'] is not Templates.aucun or not templateFilename.exists():
            self._logger.debug(f'Reading template: {templateFilename}')

            with open(str(templateFilename), 'r', newline=self.NEWLINE) as template:
                contents = template.read()

        if self._results['template'].value >= 2:
            self._logger.debug(f'Using template for {self._results["template"]}')
            nPeople = self._results['template'].value

            contents = contents.replace('* eau',
                                        f"""+------------+-------------+---------------------------------------------------+
| 1 personne | {nPeople} personnes |                                                   |
+============+=============+===================================================+
|          1 |           A | eau                                               |
+------------+-------------+---------------------------------------------------+""")

        indexString = self._results['title']

        if self._category is not Categories.cuisine:
            indexString = f'{self._category.name}; {indexString}'

        with open(str(self._results['filename']), 'w', newline=self.NEWLINE) as newFile:
            newFile.write(f'.. index:: {indexString}\n')
            newFile.write(f'.. _{self._results["category"].name}_{self._results["basename"].replace(".rst", "")}:\n')

            newFile.write('\n')
            newFile.write(self._results['title'] + '\n')
            newFile.write('#' * len(self._results['title']) + '\n')

            newFile.write(contents)

    def _createUtilisationFile(self):
        """
        Create a file for utilisation category.
        """
        with open(str(self._results['filename']), 'w', newline=self.NEWLINE) as newFile:
            newFile.write(f'.. index:: {self._results["title"]}\n')
            newFile.write(f'.. _{self._results["title"]}:\n')

            newFile.write('\n')
            newFile.write(self._results['title'] + '\n')
            newFile.write('#' * len(self._results['title']) + '\n')
            newFile.write('\n')

    def createFile(self):
        """
        Create file from template (except if file exists).
        """
        if self._results['filename'].exists():
            self._logger.debug(f'File {self._results["filename"]} already exists, skipping creation from template')
            return

        if self._results['category'] is Categories.utilisation:
            self._createUtilisationFile()

            print('WARNING: you must manually edit utilisation/index.rst '
                  f'to add the new file {self._results["filename"]}')

        else:
            self._createDefaultFile()

    def gitStageFiles(self):
        """
        Stage touched files to git for the next commit.
        """
        command = ['git', 'add', str(self._results['filename'])]
        self._logger.debug(' '.join(command))
        run(command)

    def confirm(self):
        """
        Confirm file is ready.
        """
        if self._title is None:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setWindowTitle('Nouvelle recette prête')

            msgBox.setText(f'La nouvelle recette peut maintenant être éditée dans:\n{self._results["filename"]}')

            msgBox.exec()

        print(self._results['filename'])

    def process(self) -> int:
        """
        Run the complete post-processing.
        """
        self.createFile()
        self.gitStageFiles()

        self.confirm()

        return self.exitCode


def main():
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
        choices=[category.name for category in Categories if category.name != 'UNDEFINED'],
        default=DEFAULT_CATEGORY.name,
        help=f'Categorie de la recette (defaut={DEFAULT_CATEGORY.name})'
    )
    parser.add_argument(
        '--template',
        choices=[template.name for template in Templates if template.name != 'UNDEFINED'],
        default=DEFAULT_TEMPLATE.name,
        help=f'Modele pour demarrer la recette (defaut={DEFAULT_TEMPLATE.name})'
    )
    args = parser.parse_args()

    # Logging
    logFormat = '%(asctime)s:%(levelname)s:%(funcName)s[%(lineno)d]:%(message)s'
    if args.verbose:
        logging.basicConfig(format=logFormat, level=logging.DEBUG)
    else:
        logging.basicConfig(format=logFormat, level=logging.INFO)

    # App
    app = App(args.title, Categories[args.category], Templates[args.template])
    app.run()
    exitCode = app.process()

    return exitCode


if __name__ == '__main__':
    sys.exit(main())
