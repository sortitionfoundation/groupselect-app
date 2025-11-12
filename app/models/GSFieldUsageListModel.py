from typing import Any

from PySide6 import QtCore
from PySide6.QtCore import Qt, QModelIndex, QPersistentModelIndex

from GSAppFieldMode import GSAppFieldMode
from GSProject import GSProject


class GSFieldUsageListModel(QtCore.QAbstractListModel):
    _project: GSProject
    _usage_mode: GSAppFieldMode

    def __init__(self, usage_mode: GSAppFieldMode):
        super(GSFieldUsageListModel, self).__init__()
        self._usage_mode = usage_mode

    # project updated
    def updated_project(self, project: GSProject):
        self._project = project
        self.layoutChanged.emit()

    def updated_fields(self):
        self._project.fields_usage[self._usage_mode] = [
            p_col_id
            for p_col_id in self._project.fields_usage[self._usage_mode]
            if p_col_id in self._project.data_handle.column_naming
        ]
        if self._usage_mode == GSAppFieldMode.Ignore:
            for p_col_id in self._project.data_handle.column_naming:
                if not any(p_col_id in self._project.fields_usage[usage_mode]
                           for usage_mode in GSAppFieldMode):
                    self._project.fields_usage[self._usage_mode].append(p_col_id)
        self.layoutChanged.emit()

    def _get_list(self):
        return self._project.fields_usage[self._usage_mode]

    def flags(self, index: QModelIndex | QPersistentModelIndex):
        if not index.isValid() or index.row() >= self.rowCount(None) or index.model() != self:
            return Qt.ItemFlag.ItemIsDropEnabled
        return (
                super(GSFieldUsageListModel, self).flags(index) |
                Qt.ItemFlag.ItemIsUserCheckable |
                Qt.ItemFlag.ItemIsDragEnabled
        )

    def supportedDropActions(self):
        return Qt.DropAction.MoveAction

    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = ...):
        if not index.isValid():
            return None
        if index.row() > self.rowCount(None):
            return None

        p_col_id = self._get_list()[index.row()]
        if role == Qt.ItemDataRole.EditRole:
            return p_col_id
        elif role == Qt.ItemDataRole.DisplayRole:
            return self._project.data_handle.column_naming[p_col_id]

    def insertRows(self, row: int, count: int, parent: QModelIndex | QPersistentModelIndex | None = None):
        self.beginInsertRows(QModelIndex(), row, row+count-1)
        self._get_list()[row:row] = [0] * count
        self.endInsertRows()
        self.layoutChanged.emit()
        return True

    def removeRows(self, row: int, count: int, parent: QModelIndex | QPersistentModelIndex | None = None):
        self.beginRemoveRows(QModelIndex(), row, row+count-1)
        del self._get_list()[row:row+count]
        self.endRemoveRows()
        self.layoutChanged.emit()
        return True

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = ...) -> int:
        if self._project is None or self._project.pdata is None:
            return 0
        return len(self._get_list())

    def setData(self, index: QModelIndex | QPersistentModelIndex, value: Any, role = Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.EditRole:
            self._get_list()[index.row()] = value

        self.layoutChanged.emit()
        return True

    def setItemData(self, index: QModelIndex | QPersistentModelIndex, roles: dict[int, Any]):
        if Qt.ItemDataRole.EditRole in roles:
            self._get_list()[index.row()] = roles[Qt.ItemDataRole.EditRole]
            return True
        else:
            return False
