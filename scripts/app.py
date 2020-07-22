#!/usr/bin/env python3
# coding=utf-8
"""
This script opens a GUI app to introduce a new recipe.
"""
import os.path
import sys
import re
from collections import OrderedDict
from argparse import ArgumentParser
import logging
from subprocess import run
from PySide2 import QtWidgets


class Recettes(QtWidgets.QDialog):
    """
    Pop-up window to create a new recette in this repo.
    """
    BUTTON_STATUS = {
        0: False,  # cancel
        1: True,  # ok
    }

    UNDEFINED = 'UNDEFINED'

    CATEGORIES = ['cuisine', 'cosmétique']
    DEFAULT_CATEGORY = 'cuisine'

    TEMPLATES = ['aucun', 'standard', 'X personnes']
    DEFAULT_TEMPLATE = 'standard'

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

        for category in self.CATEGORIES:
            self._categories[category] = QtWidgets.QRadioButton(category)

        self._categories[self.DEFAULT_CATEGORY].setChecked(True)

        for category in self.CATEGORIES:
            layout.addWidget(self._categories[category])

        categories = QtWidgets.QGroupBox('Catégorie')
        categories.setLayout(layout)

        return categories

    def getCategory(self) -> str:
        """
        Read which category is selected.
        """
        logString = 'categories:'
        for category in self.CATEGORIES:
            logString += ' {}'.format(category) + '={}'.format(self._categories[category].isChecked())

        self._logger.debug(logString)

        for category in self.CATEGORIES:
            if self._categories[category].isChecked():
                return category

        return self.UNDEFINED

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
        self._logger.debug('title={}'.format(title))
        return title

    @property
    def basename(self) -> str:
        """
        Get the filename for the new recipe WITHOUT the prefixed dirname.
        """
        self._logger.debug('Prepare filename')

        title = self.getTitle().strip()

        self._logger.debug('title={}'.format(title))

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
        title = title.replace("'", '_')

        # Get rid of non-standard characters
        title = re.sub(r'()\[\]{}"\/:;.,?!<>+&%=$°§ßµ', '', title)

        self._logger.debug('title formatted: {}'.format(title))

        return title

    @property
    def filename(self) -> str:
        """
        Get the filename for the new recipe.
        """
        filename = os.path.join(self.getCategory(), self.basename + '.rst')

        self._logger.debug('filename={}'.format(filename))

        return filename

    def templates(self) -> QtWidgets.QGroupBox:
        """
        Sets the template as radio buttons.
        """
        self._logger.debug('Setting templates widget')

        layout = QtWidgets.QVBoxLayout()

        templates = QtWidgets.QGroupBox('Modèle')

        self._templates = {}
        for template in self.TEMPLATES:
            self._templates[template] = QtWidgets.QRadioButton(template)

        self._templates[self.DEFAULT_TEMPLATE].setChecked(True)

        for template in self.TEMPLATES:
            layout.addWidget(self._templates[template])

        templates.setLayout(layout)

        return templates

    def getTemplate(self) -> str:
        """
        Read which template is selected.
        """
        logString = 'templates:'
        for template in self.TEMPLATES:
            logString += ' {}'.format(template) + '={}'.format(self._templates[template].isChecked())

        self._logger.debug(logString)

        for template in self.TEMPLATES:
            if self._templates[template].isChecked():
                return template

        return self.UNDEFINED

    def isTitleEmpty(self) -> bool:
        """
        Check if title is empty.
        """
        emptyTitle = bool(self.getTitle() == '')
        self._logger.debug('title is empty={}'.format(emptyTitle))
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

    def confirmUseExistingFile(self, filename: str) -> bool:
        """
        Ask user if existing file is the one to use.

        Returns:
            False if user does not want to use existing one.
        """
        self._logger.debug('File {} exists, ask user confirmation to use it'.format(filename))

        msgBox = QtWidgets.QMessageBox()

        msgBox.setWindowTitle('{} existe...'.format(filename))
        msgBox.setText('Le fichier {} existe déjà. Est-ce bien celui que tu veux éditer?'.format(filename))

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

        filename = self.filename
        if os.path.exists(filename) and not self.confirmUseExistingFile(filename):
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
        self._logger.debug('Clicked on OK={}'.format(buttonStatus))
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
            ('filename', self.filename),
            ('basename', self.basename),
        ])


class App:
    """
    Main app handling post-processing too.
    """
    NEWLINE = '\n'

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)

        self._results = OrderedDict([
            ('exitCode', None),
            ('category', 'UNDEFINED'),
        ])

    @property
    def exitCode(self):
        """
        Get the exit code.
        """
        return self._results['exitCode']

    @property
    def indexRst(self) -> str:
        """
        Get the relevant ``xxx/index.rst`` filename.
        """
        return os.path.join(self._results['category'], 'index.rst')

    def run(self) -> None:
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

        self._logger.debug(self._results)

    def createFile(self) -> None:
        """
        Create file from template (except if file exists).
        """
        if os.path.exists(self._results['filename']):
            self._logger.debug('File already exists, skipping creation from template')
            return

        contents = ''

        if self._results['template'] != 'aucun' or not os.path.exists(templateFilename):
            templateFilename = os.path.join(os.path.dirname(__file__), 'template.rst')
            self._logger.debug('Reading template: {}'.format(templateFilename))

            with open(templateFilename, 'r') as template:
                contents = template.read()

        if self._results['template'] == 'X personnes':
            self._logger.debug('Using template for X personnes')
            contents = contents.replace('* eau', """+------------+-------------+----------------------------------------------------+
| 1 personne | ? personnes |                                                    |
+============+=============+====================================================+
|          1 |           A | eau                                                |
+------------+-------------+----------------------------------------------------+""")

        with open(self._results['filename'], 'w') as newFile:
            newFile.write(self._results['title'] + '\n')
            newFile.write('#' * len(self._results['title']) + '\n')

            newFile.write(contents)

    def updateIndex(self) -> None:
        """
        Update the relevant index file to insert the new recipe.
        """
        with open(self.indexRst, 'r') as indexFile:
            indexContents = indexFile.readlines()

        header = []
        footer = []
        files = []

        # Look for toctree
        iLine = 0  # init at beginning
        for iLine in range(iLine, len(indexContents)):
            line = indexContents[iLine]
            header.append(line)

            if line == '.. toctree::{}'.format(self.NEWLINE):
                break

        # Now look for empty line
        for iLine in range(iLine + 1, len(indexContents)):
            line = indexContents[iLine]
            header.append(line)

            if line == self.NEWLINE:
                break

        # From here until empty line, it is list of files
        for iLine in range(iLine + 1, len(indexContents)):
            line = indexContents[iLine]
            files.append(line)

            if line == self.NEWLINE:
                break

        # Footer
        for iLine in range(iLine + 1, len(indexContents)):
            line = indexContents[iLine]
            footer.append(line)

        # READING DONE

        # Introduce new files and sort again
        files.append('   {}{}'.format(self._results['basename'], self.NEWLINE))
        files.sort()

        # Rewrite
        with open(self.indexRst, 'w', newline=self.NEWLINE) as indexFile:
            indexFile.write(''.join(header))
            indexFile.write(''.join(files))
            indexFile.write(''.join(footer))

    def gitStageFiles(self) -> None:
        """
        Stage touched files to git for the next commit.
        """
        command = ['git', 'add', self._results['filename'], self.indexRst]
        self._logger.debug(' '.join(command))
        run(command)

    def confirm(self) -> None:
        """
        Confirm file is ready.
        """
        msgBox = QtWidgets.QMessageBox()
        msgBox.setWindowTitle('Nouvelle recette prête')
        msgBox.setText('La nouvelle recette peut maintenant être éditée dans:\n{}'.format(self._results['filename']))
        msgBox.exec()

    def process(self) -> int:
        """
        Run the complete post-processing.
        """
        self.createFile()
        self.updateIndex()
        self.gitStageFiles()

        self.confirm()

        return self.exitCode


def main() -> None:
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
    args = parser.parse_args()

    # Logging
    logFormat = '%(asctime)s:%(levelname)s:%(funcName)s[%(lineno)d]:%(message)s'
    if args.verbose:
        logging.basicConfig(format=logFormat, level=logging.DEBUG)
    else:
        logging.basicConfig(format=logFormat, level=logging.INFO)

    # App
    app = App()
    app.run()
    exitCode = app.process()

    return exitCode


if __name__ == '__main__':
    sys.exit(main())

