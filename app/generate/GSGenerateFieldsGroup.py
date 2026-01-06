from typing import TYPE_CHECKING

from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QGroupBox, QListView

from GSAppFieldMode import GSAppFieldMode
from models.GSFieldUsageListModel import GSFieldUsageListModel

if TYPE_CHECKING:
    from base_app.AppContext import AppContext


class GSGenerateFieldsGroup(QGroupBox):
    _ctx: 'AppContext'

    def __init__(self, ctx: 'AppContext'):
        super(GSGenerateFieldsGroup, self).__init__('Field Settings')
        self._ctx = ctx

        self._create_ui()

    def _create_ui(self):
        horizontal_layout = QHBoxLayout()
        for usage_mode in GSAppFieldMode:
            if usage_mode.name[0:3] == 'Div':
                name = usage_mode.name.replace('_', ' ')
            else:
                name = usage_mode.name
            horizontal_layout.addWidget(self._create_list(
                f"{name} Fields",
                self._ctx.model_manager[f"fu{usage_mode.name.lower()}"],
            ))
        self.setLayout(horizontal_layout)

    def _create_list(self, name: str, model: GSFieldUsageListModel):
        list = QListView()
        list.setModel(model)
        list.setDragEnabled(True)
        list.setAcceptDrops(True)
        list.setDropIndicatorShown(True)
        #list.setDragDropMode(QAbstractItemView.DragDrop)
        #list.setDefaultDropAction(Qt.MoveAction)
        #list.setMovement(QListView.Snap)

        layout = QVBoxLayout()
        layout.addWidget(list)
        group = QGroupBox(name)
        group.setLayout(layout)

        return group
