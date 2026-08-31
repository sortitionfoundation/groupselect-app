"""Group box for viewing/adding/removing manual participant pre-assignments."""

from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QListView,
    QMessageBox,
)

from generate.GSManualDialog import GSManualDialog

if TYPE_CHECKING:
    from base_app.AppContext import AppContext


class GSManualAllocationsGroup(QGroupBox):
    """Group box listing manual participant-to-group pre-assignments."""

    _ctx: "AppContext"

    def __init__(self, ctx: "AppContext"):
        """Initialise the group box and build the manual-allocations UI."""
        super(GSManualAllocationsGroup, self).__init__("Manual assignments")
        self._ctx = ctx
        self.setToolTip(
            "Pre-assign specific participants to specific groups before "
            "generating; these placements are never changed by the "
            "algorithm."
        )

        self._create_ui()

    def _create_ui(self):
        self._manuals_list = QListView()
        self._manuals_list.setModel(self._ctx.model_manager["almanuals"])
        self._manuals_list.setToolTip(
            "Participants pre-assigned to a specific group. These "
            "assignments are honored by the algorithm and never moved."
        )

        self._btn_add_manual = QPushButton("Add")
        self._btn_add_manual.setToolTip(
            "Pre-assign a participant to a specific group before running "
            "the algorithm."
        )
        self._btn_add_manual.clicked.connect(self._button_clicked)
        self._btn_del_manual = QPushButton("Delete")
        self._btn_del_manual.setToolTip(
            "Remove the selected manual assignment above."
        )
        self._btn_del_manual.clicked.connect(self._button_clicked)

        manual_btns_list = QHBoxLayout()
        manual_btns_list.addWidget(self._btn_add_manual)
        manual_btns_list.addWidget(self._btn_del_manual)
        manual_btns_list_widget = QWidget()
        manual_btns_list_widget.setLayout(manual_btns_list)

        layout = QVBoxLayout()
        layout.addWidget(self._manuals_list)
        layout.addWidget(manual_btns_list_widget)
        self.setLayout(layout)

    def _button_clicked(self):
        sender = self.sender()
        if sender == self._btn_add_manual:
            try:
                allocatables = self._ctx.model_manager[
                    "almanuals"
                ].get_allocatables()
                groups = self._ctx.model_manager["almanuals"].get_groups()
            except Exception as ex:
                QMessageBox.critical(
                    self._ctx.main_window, "Error", f"Error: {ex}"
                )
                return
            ok, participant, group = GSManualDialog.get_input(
                self, allocatables, groups
            )
            if not ok:
                return
            self._ctx.model_manager["almanuals"].add_manual(participant, group)
        elif sender == self._btn_del_manual:
            model = self._ctx.model_manager["almanuals"]
            if not self._manuals_list.selectedIndexes():
                return
            model.remove_manual(self._manuals_list.currentIndex().row())
        else:
            raise Exception("Unknown button pressed.")
