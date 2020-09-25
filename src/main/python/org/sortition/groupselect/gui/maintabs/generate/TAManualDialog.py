from PyQt5.QtWidgets import QDialog, QPushButton, QComboBox, QFormLayout, QLabel, QWidget, QHBoxLayout, QVBoxLayout

class TAManualDialog(QDialog):
    def __init__(self, parent, peopleList, tables):
        super(TAManualDialog, self).__init__(parent)

        self.ok = False

        self.cb1 = QComboBox()
        for i,p in peopleList:
            self.cb1.addItem(p, i)
        self.cb2 = QComboBox()
        for t in range(tables):
            self.cb2.addItem("Table {}".format(t+1), t)

        label1 = QLabel("Person:")
        label2 = QLabel("Table:")

        form = QFormLayout()
        form.addRow(label1, self.cb1)
        form.addRow(label2, self.cb2)
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
        return (dialog.ok, dialog.cb1.currentData(), dialog.cb2.currentData())
