from PyQt5.QtWidgets import QDialog, QPushButton, QLineEdit, QFormLayout, QLabel, QWidget, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QIntValidator, QDoubleValidator

class TAAdvancedSettingsDialog(QDialog):
    def __init__(self, parent, attempts_default, seed_default):
        super(TAAdvancedSettingsDialog, self).__init__(parent)

        self.ok = False

        self.attempts_field = QLineEdit()
        self.attempts_field.setValidator( QIntValidator(1, 1000, self) );
        self.attempts_field.setText(str(attempts_default))

        self.seed_field = QLineEdit()
        self.seed_field.setValidator( QDoubleValidator() );
        self.seed_field.setText(str(seed_default))

        form = QFormLayout()
        form.addRow(QLabel("Number of Attempts:"), self.attempts_field)
        form.addRow(QLabel("Random Number Seed:"), self.seed_field)
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
    def get_input(cls, parent, attempts_default, seed_default):
        dialog = cls(parent, attempts_default, seed_default)
        dialog.exec_()
        return (dialog.ok, int(dialog.attempts_field.text()) if dialog.attempts_field.text() else attempts_default, float(dialog.seed_field.text()) if dialog.seed_field.text() else seed_default)
