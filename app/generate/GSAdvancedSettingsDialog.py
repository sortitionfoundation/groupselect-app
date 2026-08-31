"""Dialog for editing advanced allocation settings.

Attempts, seed, swap rounds, and cluster tables -- not every algorithm uses
all of these (see `GSProject.ALGORITHM_SETTINGS`), so the fields not used by
the currently-chosen algorithm are shown greyed out/inactive rather than
hidden.
"""

from PySide6.QtWidgets import (
    QDialog,
    QPushButton,
    QLineEdit,
    QFormLayout,
    QLabel,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
)
from PySide6.QtGui import QIntValidator, QDoubleValidator

from groupselect import Algorithm

from GSProject import ALGORITHM_SETTINGS


class GSAdvancedSettingsDialog(QDialog):
    """Modal dialog for editing attempts, seed, swap rounds, cluster tables."""

    _ok: bool = False

    def __init__(
        self,
        parent,
        algorithm: Algorithm,
        attempts_default: int,
        seed_default: float,
        swap_rounds_default: int,
        cluster_tables_default: int,
    ):
        """Initialise the dialog and build the form UI."""
        super(GSAdvancedSettingsDialog, self).__init__(parent)

        self._create_ui(
            attempts_default,
            seed_default,
            swap_rounds_default,
            cluster_tables_default,
        )
        self._apply_algorithm(algorithm)

    def _create_ui(
        self,
        attempts_default: int,
        seed_default: float,
        swap_rounds_default: int,
        cluster_tables_default: int,
    ):
        self._attempts_field = QLineEdit()
        self._attempts_field.setValidator(QIntValidator(1, 1000, self))
        self._attempts_field.setText(str(attempts_default))
        self._attempts_label = QLabel("Number of attempts:")

        self._seed_field = QLineEdit()
        self._seed_field.setValidator(QDoubleValidator())
        self._seed_field.setText(str(seed_default))
        self._seed_label = QLabel("Random number seed:")

        self._swap_rounds_field = QLineEdit()
        self._swap_rounds_field.setValidator(QIntValidator(1, 1000, self))
        self._swap_rounds_field.setText(str(swap_rounds_default))
        self._swap_rounds_label = QLabel("Swap rounds:")

        self._cluster_tables_field = QLineEdit()
        self._cluster_tables_field.setValidator(QIntValidator(0, 1000, self))
        self._cluster_tables_field.setText(str(cluster_tables_default))
        self._cluster_tables_label = QLabel("Cluster tables:")

        form = QFormLayout()
        form.addRow(self._attempts_label, self._attempts_field)
        form.addRow(self._seed_label, self._seed_field)
        form.addRow(self._swap_rounds_label, self._swap_rounds_field)
        form.addRow(self._cluster_tables_label, self._cluster_tables_field)
        form_widget = QWidget()
        form_widget.setLayout(form)

        self._btn_ok = QPushButton("Ok")
        self._btn_ok.clicked.connect(self._button_press)
        self._btn_cancel = QPushButton("Cancel")
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

    def _apply_algorithm(self, algorithm: Algorithm) -> None:
        """Grey out fields the given algorithm doesn't read."""
        used = ALGORITHM_SETTINGS[algorithm]
        for key, field, label in [
            ("n_attempts", self._attempts_field, self._attempts_label),
            ("seed", self._seed_field, self._seed_label),
            ("swap_rounds", self._swap_rounds_field, self._swap_rounds_label),
            (
                "cluster_tables",
                self._cluster_tables_field,
                self._cluster_tables_label,
            ),
        ]:
            enabled = key in used
            field.setEnabled(enabled)
            label.setEnabled(enabled)

    def _button_press(self):
        if self.sender() == self._btn_ok:
            self._ok = True
        self.close()

    @classmethod
    def get_input(
        cls,
        parent,
        algorithm: Algorithm,
        attempts_default: int,
        seed_default: float,
        swap_rounds_default: int,
        cluster_tables_default: int,
    ):
        """Show the dialog modally and return the (ok, *fields) tuple."""
        dialog = cls(
            parent,
            algorithm,
            attempts_default,
            seed_default,
            swap_rounds_default,
            cluster_tables_default,
        )
        dialog.exec_()
        return (
            dialog._ok,
            int(dialog._attempts_field.text())
            if dialog._attempts_field.text()
            else attempts_default,
            float(dialog._seed_field.text())
            if dialog._seed_field.text()
            else seed_default,
            int(dialog._swap_rounds_field.text())
            if dialog._swap_rounds_field.text()
            else swap_rounds_default,
            int(dialog._cluster_tables_field.text())
            if dialog._cluster_tables_field.text()
            else cluster_tables_default,
        )
