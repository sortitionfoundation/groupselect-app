from PyQt5 import QtWidgets
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QVBoxLayout, QRadioButton, QHBoxLayout, QLabel, QPushButton, QWidget, QFormLayout, QLineEdit


class TANewFileOptionsDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super(TANewFileOptionsDialog, self).__init__(parent)

        self.__ok = False

        self.__number = 20
        self.__names = "name,gender,age"

        self.__createUi()

    def __createUi(self):
        label = QLabel('Please select the CSV format.', self)

        label1 = QLabel("Number of entries:")
        label2 = QLabel("Field names:")

        self.__numberField = QLineEdit()
        self.__numberField.setValidator(QIntValidator(1, 10000, self))
        self.__numberField.setText(str(self.__number))

        self.__nameField = QLineEdit()
        self.__nameField.setText(self.__names)

        form = QFormLayout()
        form.addRow(label1, self.__numberField)
        form.addRow(label2, self.__nameField)
        form_widget = QWidget()
        form_widget.setLayout(form)

        self.__btnOk = QPushButton("Ok")
        self.__btnOk.clicked.connect(self.__buttonPress)
        self.__btnCancel = QPushButton("Cancel")
        self.__btnCancel.clicked.connect(self.__buttonPress)
        self.__btnCancel.move(80, 0)

        buttons = QHBoxLayout()
        buttons.addWidget(self.__btnOk)
        buttons.addWidget(self.__btnCancel)
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons)

        layout = QVBoxLayout()
        layout.addWidget(buttons_widget)

        vbox = QVBoxLayout()
        vbox.addWidget(label)
        vbox.addWidget(form_widget)
        vbox.addSpacing(15)
        vbox.addWidget(buttons_widget)
        self.setLayout(vbox)

    def __buttonPress(self):
        self.__ok = self.sender() == self.__btnOk

        self.__number = int(self.__numberField.text())
        self.__names = self.__nameField.text()

        self.close()

    @classmethod
    def get_input(cls, parent):
        dialog = cls(parent)
        dialog.exec_()
        return (dialog.__ok, dialog.__number, dialog.__names)