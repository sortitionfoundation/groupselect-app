"""Group box for assigning field usage modes via drag-and-drop lists."""

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QGroupBox, QListView

from GSAppFieldMode import GSAppFieldMode, FIELD_MODE_LABELS
from models.GSFieldUsageListModel import GSFieldUsageListModel

if TYPE_CHECKING:
    from base_app.AppContext import AppContext


class GSGenerateFieldsGroup(QGroupBox):
    """Group box with one drag-and-drop list of fields per usage mode."""

    _ctx: "AppContext"

    def __init__(self, ctx: "AppContext"):
        """Initialise the group box and build the field lists."""
        super(GSGenerateFieldsGroup, self).__init__("Field Settings")
        self._ctx = ctx

        self._create_ui()

    def _create_ui(self):
        horizontal_layout = QHBoxLayout()
        for usage_mode in GSAppFieldMode:
            horizontal_layout.addWidget(
                self._create_list(
                    FIELD_MODE_LABELS[usage_mode],
                    self._ctx.model_manager[f"fu{usage_mode.name.lower()}"],
                )
            )
        self.setLayout(horizontal_layout)

    def _create_list(self, name: str, model: GSFieldUsageListModel):
        list = QListView()
        list.setModel(model)
        list.setDragEnabled(True)
        list.setAcceptDrops(True)
        list.setDropIndicatorShown(True)
        # list.setDragDropMode(QAbstractItemView.DragDrop)
        # list.setDefaultDropAction(Qt.MoveAction)
        # list.setMovement(QListView.Snap)

        layout = QVBoxLayout()
        layout.addWidget(list)
        group = QGroupBox(name)
        group.setLayout(layout)

        return group
