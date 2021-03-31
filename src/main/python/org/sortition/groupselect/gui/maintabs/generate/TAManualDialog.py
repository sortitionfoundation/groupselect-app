from PyQt5.QtWidgets import QDialog, QPushButton, QComboBox, QFormLayout, QLabel, QWidget, QHBoxLayout, QVBoxLayout

class TAManualDialog(QDialog):
    def __init__(self, parent, people_list, group_list):
        super(TAManualDialog, self).__init__(parent)

        self.ok = False

        self.cb1 = QComboBox()
        for pid, plabel in people_list:
            self.cb1.addItem(plabel, pid)
        self.cb2 = QComboBox()
        for gid, glabel in group_list:
            self.cb2.addItem(glabel, gid)

        label1 = QLabel("Person:")
        label2 = QLabel("Group:")

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
    def get_input(cls, parent, people_list, group_list):
        dialog = cls(parent, people_list, group_list)
        dialog.exec_()
        return (dialog.ok, dialog.cb1.currentData(), dialog.cb2.currentData())
