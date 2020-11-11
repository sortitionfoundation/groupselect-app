from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QVBoxLayout, QRadioButton, QHBoxLayout, QLabel, QPushButton, QWidget


class TAImportOptionsDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super(TAImportOptionsDialog, self).__init__(parent)

        self.initUI()

    def initUI(self):

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()

        self.label = QLabel('Please select the CSV format.', self)

        self.rb1 = QRadioButton("Automatic detection", self)
        self.rb1.setChecked(True)
        self.rb2 = QRadioButton("Comma delimiter", self)
        self.rb3 = QRadioButton("Semicolon delimiter", self)

        hbox.addWidget(self.rb1)
        hbox.addWidget(self.rb2)
        hbox.addWidget(self.rb3)

        self.btn_ok = QPushButton("Ok")
        self.btn_ok.clicked.connect(self.button_press)
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.button_press)
        self.btn_cancel.move(80, 0)

        buttons = QHBoxLayout()
        buttons.addWidget(self.btn_ok)
        buttons.addWidget(self.btn_cancel)
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons)

        layout = QVBoxLayout()
        layout.addWidget(buttons_widget)

        vbox.addSpacing(15)

        vbox.addLayout(hbox)
        vbox.addWidget(self.label)
        vbox.addWidget(buttons_widget)
        self.setLayout(vbox)

    def button_press(self):
        if self.sender() == self.btn_ok:
            self.ok = True
            if(self.rb1.isChecked()):
                self.radio_status = 'auto'
            elif(self.rb2.isChecked()):
                self.radio_status = 'comma'
            elif(self.rb3.isChecked()):
                self.radio_status = 'semicolon'
            else:
                self.radio_status = 'auto'
        else:
            self.ok = True
            self.radio_status = ''
        self.close()

    @classmethod
    def get_input(cls, parent):
        dialog = cls(parent)
        dialog.exec_()
        return (dialog.ok, dialog.radio_status)