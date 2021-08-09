from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QVBoxLayout, QRadioButton, QHBoxLayout, QLabel, QPushButton, QWidget, QTableWidget


class TAImportOptionsDialog(QtWidgets.QDialog):
    def __init__(self, parent, data_action_handler: 'TAMainWindowDataActionHandler', file_lines: list):
        super(TAImportOptionsDialog, self).__init__(parent)

        self.__dataActionHandler = data_action_handler
        self.__fileLines = file_lines

        self.__setupUi()

        self.__updateTableData()

    def __setupUi(self):
        # radios
        radioButtonLayout = QHBoxLayout()
        self.rb1 = QRadioButton("Automatic", self)
        self.rb2 = QRadioButton("Comma", self)
        self.rb3 = QRadioButton("Semicolon", self)
        self.rb1.setChecked(True)
        radioButtonLayout.addWidget(QLabel('Delimiter:', self))
        radioButtonLayout.addWidget(self.rb1)
        radioButtonLayout.addWidget(self.rb2)
        radioButtonLayout.addWidget(self.rb3)

        # table
        self.table = QTableWidget()
        #self.tablesetEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        # buttons
        self.btn_ok = QPushButton("Ok")
        self.btn_ok.clicked.connect(self.__radioButtonPress)
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.__radioButtonPress)
        self.btn_cancel.move(80, 0)

        buttons = QHBoxLayout()
        buttons.addWidget(self.btn_ok)
        buttons.addWidget(self.btn_cancel)
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons)

        layout = QVBoxLayout()
        layout.addWidget(buttons_widget)

        vbox = QVBoxLayout()
        vbox.addSpacing(15)
        vbox.addWidget(QLabel('Please specify how the CSV file should be imported.', self))
        vbox.addLayout(radioButtonLayout)
        vbox.addWidget(self.table)
        vbox.addWidget(buttons_widget)
        self.setLayout(vbox)

    def __radioButtonPress(self):
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
            self.ok = False
            self.radio_status = ''
        self.close()

    def collectOptions(self):
        options = {}

        if(self.rb1.isChecked()):
            options['csv_format'] = 'auto'
        elif(self.rb2.isChecked()):
            options['csv_format'] = 'comma'
        elif(self.rb3.isChecked()):
            options['csv_format'] = 'semicolon'
        else:
            options['csv_format'] = 'auto'

        return options

    def __updateTableData(self):
        self.__dataActionHandler.importRawWithOptions(self.__fileLines, self.collectOptions())

    @classmethod
    def get_input(cls, parent, data_action_handler: 'TAMainWindowDataActionHandler', file_lines: list):
        dialog = cls(parent, data_action_handler, file_lines)
        dialog.exec_()
        return (dialog.ok, dialog.collectOptions())