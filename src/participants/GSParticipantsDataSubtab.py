from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QTableView, QMenu, QInputDialog

from base_app.AppContext import AppContext


class GSParticipantsDataSubtab(QTableView):
    def __init__(self, ctx: AppContext):
        super(GSParticipantsDataSubtab, self).__init__()
        self._ctx = ctx

        self.setModel(self._ctx.model_manager['pdata'])

        self.horizontalHeader().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.horizontalHeader().customContextMenuRequested.connect(self._horizontal_header_menu_popup)

    def _horizontal_header_menu_popup(self, pos):
        # Find the clicked column.
        col_index = self.columnAt(pos.x())
        col_naming = self._ctx.project_manager.project.data_handle.column_naming
        col_id = list(col_naming)[col_index]
        col_name = col_naming[col_id]

        # Create the context menu.
        menu = QMenu()
        action_rename = QAction('Rename', self)
        menu.addAction(action_rename)
        action_use = QAction('Disable', self)
        menu.addAction(action_use)

        # Open context menu and read action.
        action_clicked = menu.exec_(self.mapToGlobal(pos))
        if action_clicked is None:
            return

        # Identify action and execute.
        if action_clicked == action_rename:
            col_name, ok = QInputDialog.getText(
                self._ctx.main_window,
                'Rename column',
                'Name:',
                text=col_name,
            )
            if ok:
                col_name = col_name or None
                col_naming[col_id] = col_name
                self._ctx.model_manager.updated_participants()
        elif action_clicked == action_use:
            del col_naming[col_id]
            self._ctx.project_manager.project.data_handle.imported_data.drop(columns=col_id, inplace=True)
            self._ctx.model_manager.updated_participants()
