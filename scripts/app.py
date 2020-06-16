#!/usr/bin/env python3
"""
.. todo:: doc
"""
import sys
from PySide2 import QtWidgets


class Recettes(QtWidgets.QMainWindow):
    """
    App to create a new recette in this repo.

    .. todo::

       * window title
       * post-actions
    """
    def category(self):
        self._category = QtWidgets.QButtonGroup()
        self._cuisine = QtWidgets.QRadioButton('cuisine', self)
        self._cosmetique = QtWidgets.QRadioButton('cosmétique', self)

    def title(self):
        self._title = QtWidgets.QText()
        self._title = QtWidgets.QLabel('Titre:', self)
        self._title.setBuddy(QtWidgets.QLineEdit(self))

    def template(self):
        self._template = QtWidgets.QButtonGroup()
        self._default = QtWidgets.QRadioButton('standard', self)
        self._personnes = QtWidgets.QRadioButton('personnes', self)
        self._plaques = QtWidgets.QRadioButton('petite et grande plaques', self)

    def buttons(self):
        """
        OK cancel
        """
        self._buttons = QtWidgets.QButtonGroup()
        self._ok = QtWidgets.QPushButton('OK', self)
        self._cancel = QtWidgets.QPushButton('annuler', self)


def main():
    """
    Main function.
    """
    app = QtWidgets.QApplication(sys.argv)
    recettes = Recettes()
    recettes.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

