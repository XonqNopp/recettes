#!/usr/bin/env python3
# coding=utf-8
"""
.. todo::

   * doc
   * post-actions
   * error if title invalid (empty)
   * error if file exists
"""
import os.path
import sys
from collections import OrderedDict
from argparse import ArgumentParser
import logging
from PySide2 import QtWidgets


class Recettes(QtWidgets.QDialog):
    """
    App to create a new recette in this repo.
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
        self._logger.debug('Setting categories widget')

        layout = QtWidgets.QVBoxLayout()

        self._categories = {}
        self._categories['cuisine'] = QtWidgets.QRadioButton('cuisine')
        self._categories['cosmetique'] = QtWidgets.QRadioButton('cosmétique')

        self._categories['cuisine'].setChecked(True)

        layout.addWidget(self._categories['cuisine'])
        layout.addWidget(self._categories['cosmetique'])

        categories = QtWidgets.QGroupBox('Catégorie')
        categories.setLayout(layout)

        return categories

    def getCategory(self) -> str:
        self._logger.debug('categories: cuisine={} cosmetique={}'.format(
            self._categories['cuisine'].isChecked(),
            self._categories['cosmetique'].isChecked()
        ))

        if self._categories['cuisine'].isChecked():
            return 'cuisine'

        if self._categories['cosmetique'].isChecked():
            return 'cosmetique'

        return 'UNDEFINED'

    def title(self) -> QtWidgets.QGroupBox:
        self._title = QtWidgets.QLineEdit()
        self._title.setFixedWidth(500)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self._title)

        title = QtWidgets.QGroupBox('Titre')
        title.setLayout(layout)

        return title

    def getTitle(self) -> str:
        return self._title.text()

    @property
    def filename(self) -> str:
        title = self.getTitle()
        filename = os.path.join(self.getCategory(), title) + '.rst'

        self._logger.debug('filename={}'.format(filename))

        return filename

    def templates(self) -> QtWidgets.QGroupBox:
        layout = QtWidgets.QVBoxLayout()

        templates = QtWidgets.QGroupBox('Modèle')

        self._templates = {}
        self._templates['NONE'] = QtWidgets.QRadioButton('aucun')
        self._templates['default'] = QtWidgets.QRadioButton('standard')
        self._templates['personnes'] = QtWidgets.QRadioButton('X personnes')
        self._templates['plaques'] = QtWidgets.QRadioButton('petite et grande plaques')

        self._templates['default'].setChecked(True)

        layout.addWidget(self._templates['NONE'])
        layout.addWidget(self._templates['default'])
        layout.addWidget(self._templates['personnes'])
        layout.addWidget(self._templates['plaques'])

        templates.setLayout(layout)

        return templates

    def getTemplate(self) -> str:
        if self._templates['default'].isChecked():
            return 'default'

        if self._templates['personnes'].isChecked():
            return 'personnes'

        if self._templates['plaques'].isChecked():
            return 'plaques'

        return 'UNDEFINED'

    def isTitleEmpty(self) -> bool:
        return self.getTitle() == ''

    def fileExists(self) -> bool:
        return os.path.exists(self.filename)

    def rejectEmptyTitle(self):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setText('Le titre ne peut pas etre vide')
        msgBox.exec()

    def rejectExistingFile(self):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setText('Il y a deja un fichier avec le meme nom: {}'.format(self.filename))
        msgBox.exec()

    def accept(self) -> None:
        if self.isTitleEmpty():
            self._logger.debug('Not accepted: title empty')
            self.rejectEmptyTitle()
            return

        if self.fileExists():
            self._logger.debug('Not accepted: file exists {}'.format(self.filename))
            self.rejectExistingFile()
            return

        super().accept()

    def buttons(self) -> QtWidgets.QDialogButtonBox:
        """
        OK cancel
        """
        self._buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self._buttons.accepted.connect(self.accept)
        self._buttons.rejected.connect(self.reject)
        return self._buttons

    def getButton(self) -> bool:
        return self.BUTTON_STATUS[self.result()]

    def getInputs(self) -> OrderedDict:
        return OrderedDict([
            ('button', self.getButton()),
            ('category', self.getCategory()),
            ('title', self.getTitle()),
            ('template', self.getTemplate()),
            ('filename', self.filename),
        ])


class App:
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)

        self._results = OrderedDict([
            ('exitCode', None),
            ('category', 'UNDEFINED'),
        ])

    @property
    def exitCode(self):
        return self._results['exitCode']

    @property
    def indexRst(self) -> str:
        return os.path.join(self._results['category'], 'index.rst')

    def run(self) -> None:
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

    @property
    def filename(self) -> str:
        return self._results['filename']

    def fileExists(self) -> bool:
        self.filename
        pass

    def createFile(self) -> None:
        pass

    def applyTemplate(self) -> None:
        pass

    def updateIndex(self) -> None:
        pass

    def gitStageFiles(self) -> None:
        pass

    def process(self) -> int:
        if self.fileExists():
            raise Exception

        self.createFile()
        self.applyTemplate()
        self.updateIndex()
        self.gitStageFiles()

        return self.exitCode


def main() -> None:
    """
    Main function.
    """
    # Parser
    parser = ArgumentParser()
    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        default=False,
    )
    args = parser.parse_args()

    # Logging
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # App
    app = App()
    app.run()
    exitCode = app.process()

    return exitCode


if __name__ == '__main__':
    sys.exit(main())

