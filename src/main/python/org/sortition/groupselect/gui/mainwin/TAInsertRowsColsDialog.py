from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QDialog, QPushButton, QComboBox, QFormLayout, QLabel, QWidget, QHBoxLayout, QVBoxLayout, \
                            QLineEdit

class TAInsertRowsColsDialog(QDialog):
    def __init__(self, parent = None, type = 'rows', options = []):
        super(TAInsertRowsColsDialog, self).__init__(parent)

        self.ok = False

        self.cb = QComboBox()
        for index,name in options:
            self.cb.addItem(str(name), index)

        self.nmb = QLineEdit()
        self.nmb.setValidator( QIntValidator(1, 1000, self) );
        self.nmb.setText('1')

        label1 = QLabel("Insert before " + ('row' if type=='rows' else 'col') + ":")
        label2 = QLabel("Number:")

        form = QFormLayout()
        form.addRow(label1, self.cb)
        form.addRow(label2, self.nmb)
        form_widget = QWidget()
        form_widget.setLayout(form)

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
        layout.addWidget(form_widget)
        layout.addWidget(buttons_widget)
        self.setLayout(layout)

    def button_press(self):
        if self.sender() == self.btn_ok:
            self.ok = True
        self.close()

    @classmethod
    def get_input(cls, parent, peopleList, tables):
        dialog = cls(parent, peopleList, tables)
        dialog.exec_()
        return (dialog.ok, dialog.cb.currentData(), int(dialog.nmb.text()))
