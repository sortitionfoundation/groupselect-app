from PySide6 import QtCore
from PySide6.QtCore import Qt
from datahandling import excel_col_name

from base_app.AbstractProjectModel import AbstractProjectModel

from GSProject import GSProject


class GSParticipantsFieldsModel(QtCore.QStringListModel, AbstractProjectModel):
    _project: GSProject

    def __init__(self):
        super(GSParticipantsFieldsModel, self).__init__()

    # project updated
    def updated_project(self, project: GSProject):
        self._project = project
        self.layoutChanged.emit()

    def data(self, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex, role: int = ...):
        if role == Qt.ItemDataRole.DisplayRole:
            col_id = list(self._project.data_handle.column_naming)[index.row()]
            return self._project.data_handle.column_naming[col_id] or excel_col_name(col_id)

    def rowCount(self, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex = ...):
        if self._project is None or self._project.pdata is None:
            return 0

        return len(self._project.data_handle.column_naming)

    def flags(self, index):
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
