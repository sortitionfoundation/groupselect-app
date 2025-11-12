from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QTableView, QMenu, QInputDialog

from importing.GSPreviewTableModel import GSPreviewTableModel

if TYPE_CHECKING:
    from GSPreviewDialog import GSPreviewDialog


class GSPreviewTableView(QTableView):
    def __init__(self, model: GSPreviewTableModel, dialogue: 'GSPreviewDialog'):
        super(GSPreviewTableView, self).__init__()
        self._model = model
        self._dialogue = dialogue

        self.setModel(model)

        self.horizontalHeader().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.horizontalHeader().customContextMenuRequested.connect(self._horizontal_header_menu)

    def _horizontal_header_menu(self, pos):
        # Find the clicked column.
        col_id = self.columnAt(pos.x())
        col_name = self._model.get_column_name(col_id)
        col_use = self._model.get_column_use(col_id)

        # Create the context menu.
        menu = QMenu()
        action_rename = QAction('Rename', menu)
        menu.addAction(action_rename)
        action_use = QAction('Disable' if col_use else 'Enable')
        menu.addAction(action_use)

        # Open context menu and read action.
        action_clicked = menu.exec_(self.mapToGlobal(pos))
        if action_clicked is None:
            return

        # Identify action and execute.
        if action_clicked == action_rename:
            col_name, ok = QInputDialog.getText(
                self._dialogue,
                'Rename column',
                'Name:',
                text=col_name,
            )
            if ok:
                col_name = col_name or None
                self._model.set_column_name(col_id, col_name)
        elif action_clicked == action_use:
            self._model.set_column_use(col_id, not col_use)
        else:
            raise Exception('Unknown action.')
