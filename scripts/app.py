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
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QtWidgets.QVBoxLayout()

        category = self.categories()
        layout.addWidget(category['cuisine'])
        layout.addWidget(category['cosmetique'])

        layout.addWidget(self.title())

        template = self.templates()
        layout.addWidget(template['default'])
        layout.addWidget(template['personnes'])
        layout.addWidget(template['plaques'])

        button = self.buttons()
        layout.addWidget(button['ok'])
        layout.addWidget(button['cancel'])

        self.setLayout(layout)

    def categories(self):
        self._categories = QtWidgets.QButtonGroup()

        cuisine = QtWidgets.QRadioButton('cuisine', self)
        cosmetique = QtWidgets.QRadioButton('cosmétique', self)

        self._categories.addButton(cuisine)
        self._categories.addButton(cosmetique)

        return {'cuisine': cuisine, 'cosmetique': cosmetique}

    def title(self):
        title = QtWidgets.QLabel('Titre:', self)
        title.setBuddy(QtWidgets.QLineEdit(self))
        return title

    def templates(self):
        self._templates = QtWidgets.QButtonGroup()

        default = QtWidgets.QRadioButton('standard', self)
        personnes = QtWidgets.QRadioButton('personnes', self)
        plaques = QtWidgets.QRadioButton('petite et grande plaques', self)

        self._templates.addButton(default)
        self._templates.addButton(personnes)
        self._templates.addButton(plaques)

        return {'default': default, 'personnes': personnes, 'plaques': plaques}

    def buttons(self):
        """
        OK cancel
        """
        self._buttons = QtWidgets.QButtonGroup()

        ok = QtWidgets.QPushButton('OK', self)
        cancel = QtWidgets.QPushButton('annuler', self)

        self._buttons.addButton(ok)
        self._buttons.addButton(cancel)

        return {'ok': ok, 'cancel': cancel}


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

