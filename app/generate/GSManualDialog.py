from PySide6.QtWidgets import QDialog, QPushButton, QComboBox, QFormLayout, QLabel, QWidget, QHBoxLayout, QVBoxLayout


class GSManualDialog(QDialog):
    _ok: bool = False

    def __init__(self, parent, allocatables: dict, groups: dict):
        super(GSManualDialog, self).__init__(parent)

        self._cb1 = QComboBox()
        for p_id, p_label in allocatables.items():
            self._cb1.addItem(p_label, p_id)
        self._cb2 = QComboBox()
        for g_id, g_label in groups.items():
            self._cb2.addItem(g_label, g_id)

        label1 = QLabel('Person:')
        label2 = QLabel('Group:')

        form = QFormLayout()
        form.addRow(label1, self._cb1)
        form.addRow(label2, self._cb2)
        form_widget = QWidget()
        form_widget.setLayout(form)

        self._btn_ok = QPushButton('Ok')
        self._btn_ok.clicked.connect(self.button_press)
        self._btn_cancel = QPushButton('Cancel')
        self._btn_cancel.clicked.connect(self.button_press)
        self._btn_cancel.move(80, 0)

        buttons = QHBoxLayout()
        buttons.addWidget(self._btn_ok)
        buttons.addWidget(self._btn_cancel)
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons)

        layout = QVBoxLayout()
        layout.addWidget(form_widget)
        layout.addWidget(buttons_widget)
        self.setLayout(layout)

    def button_press(self):
        if self.sender() == self._btn_ok:
            self._ok = True
        self.close()

    @classmethod
    def get_input(cls, parent: QWidget, allocatables: dict, groups: dict):
        dialog = cls(parent, allocatables, groups)
        dialog.exec_()
        return dialog._ok, dialog._cb1.currentData(), dialog._cb2.currentData()
