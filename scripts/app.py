#!/usr/bin/env python3
# coding=utf-8
"""
.. todo:: doc
"""
import sys
from PySide2 import QtWidgets


class Recettes(QtWidgets.QDialog):
    """
    App to create a new recette in this repo.

    .. todo::

       * post-actions
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(self.categories())
        layout.addWidget(self.title())
        layout.addWidget(self.templates())
        layout.addWidget(self.buttons())

        self.setLayout(layout)

        self.setWindowTitle('Ajouter une nouvelle recette')
        #self.resize(800, 600)

    def categories(self):
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

    def title(self):
        self._title = QtWidgets.QLineEdit()
        self._title.setFixedWidth(500)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self._title)

        title = QtWidgets.QGroupBox('Titre')
        title.setLayout(layout)

        return title

    def templates(self):
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

    def buttons(self):
        """
        OK cancel
        """
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        return buttons

    def getCategory(self):
        if self._categories['cuisine'].isChecked():
            return 'cuisine'

        if self._categories['cosmetique'].isChecked():
            return 'cosmetique'

        return 'UNDEFINED'

    def getTitle(self):
        return self._title.text()

    def getTemplate(self):
        if self._templates['default'].isChecked():
            return 'default'

        if self._templates['personnes'].isChecked():
            return 'personnes'

        if self._templates['plaques'].isChecked():
            return 'plaques'

        return 'UNDEFINED'

    def getInputs(self):
        return {
            'category': self.getCategory(),
            'title': self.getTitle(),
            'template': self.getTemplate(),
        }


def main():
    """
    Main function.
    """
    app = QtWidgets.QApplication(sys.argv)
    recettes = Recettes()
    recettes.show()
    exitCode = app.exec_()
    print(recettes.getInputs())
    sys.exit(exitCode)


if __name__ == '__main__':
    main()

