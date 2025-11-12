from PySide6.QtWidgets import QDialog, QPushButton, QLineEdit, QFormLayout, QLabel, QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtGui import QIntValidator, QDoubleValidator


class GSAdvancedSettingsDialog(QDialog):
    _ok: bool = False

    def __init__(self, parent, attempts_default: int, seed_default: float):
        super(GSAdvancedSettingsDialog, self).__init__(parent)

        self._create_ui(attempts_default, seed_default)

    def _create_ui(self, attempts_default: int, seed_default: float):
        self._attempts_field = QLineEdit()
        self._attempts_field.setValidator(QIntValidator(1, 1000, self))
        self._attempts_field.setText(str(attempts_default))

        self._seed_field = QLineEdit()
        self._seed_field.setValidator(QDoubleValidator())
        self._seed_field.setText(str(seed_default))

        form = QFormLayout()
        form.addRow(QLabel('Number of Attempts:'), self._attempts_field)
        form.addRow(QLabel('Random Number Seed:'), self._seed_field)
        form_widget = QWidget()
        form_widget.setLayout(form)

        self._btn_ok = QPushButton('Ok')
        self._btn_ok.clicked.connect(self._button_press)
        self._btn_cancel = QPushButton('Cancel')
        self._btn_cancel.clicked.connect(self._button_press)
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

    def _button_press(self):
        if self.sender() == self._btn_ok:
            self.ok = True
        self.close()

    @classmethod
    def get_input(cls, parent, attempts_default: int, seed_default: float):
        dialog = cls(parent, attempts_default, seed_default)
        dialog.exec_()
        return (
            dialog._ok,
            int(dialog._attempts_field.text()) if dialog._attempts_field.text() else attempts_default,
            float(dialog._seed_field.text()) if dialog._seed_field.text() else seed_default,
        )
