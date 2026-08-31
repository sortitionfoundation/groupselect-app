"""List model of the fields assigned to one field usage mode."""

from typing import Any

from PySide6 import QtCore
from PySide6.QtCore import Qt, QModelIndex, QPersistentModelIndex

from GSAppFieldMode import GSAppFieldMode
from GSProject import GSProject


class GSFieldUsageListModel(QtCore.QAbstractListModel):
    """Drag-and-drop list of the fields currently in one usage mode."""

    _project: GSProject
    _usage_mode: GSAppFieldMode

    def __init__(self, usage_mode: GSAppFieldMode):
        """Initialise the model for a given field usage mode."""
        super(GSFieldUsageListModel, self).__init__()
        self._usage_mode = usage_mode

    # project updated
    def updated_project(self, project: GSProject):
        """Bind the model to a (newly opened) project."""
        self._project = project
        self.layoutChanged.emit()

    def updated_fields(self):
        """Drop fields no longer present and add any newly unassigned ones."""
        self._project.fields_usage[self._usage_mode] = [
            p_col_id
            for p_col_id in self._project.fields_usage[self._usage_mode]
            if p_col_id in self._project.data_handle.column_naming
        ]
        if self._usage_mode == GSAppFieldMode.Ignore:
            for p_col_id in self._project.data_handle.column_naming:
                if not any(
                    p_col_id in self._project.fields_usage[usage_mode]
                    for usage_mode in GSAppFieldMode
                ):
                    self._project.fields_usage[self._usage_mode].append(
                        p_col_id
                    )
        self.layoutChanged.emit()

    def _get_list(self):
        return self._project.fields_usage[self._usage_mode]

    def flags(self, index: QModelIndex | QPersistentModelIndex):
        """Return flags allowing checking, dragging, and dropping of items."""
        if (
            not index.isValid()
            or index.row() >= self.rowCount(None)
            or index.model() != self
        ):
            return Qt.ItemFlag.ItemIsDropEnabled
        return (
            super(GSFieldUsageListModel, self).flags(index)
            | Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsDragEnabled
        )

    def supportedDropActions(self):
        """Support only move actions, since drops reassign field usage."""
        return Qt.DropAction.MoveAction

    def data(
        self, index: QModelIndex | QPersistentModelIndex, role: int = ...
    ):
        """Return the field's column ID or its display name."""
        if not index.isValid():
            return None
        if index.row() > self.rowCount(None):
            return None

        p_col_id = self._get_list()[index.row()]
        if role == Qt.ItemDataRole.EditRole:
            return p_col_id
        elif role == Qt.ItemDataRole.DisplayRole:
            return self._project.data_handle.column_naming[p_col_id]

    def insertRows(
        self,
        row: int,
        count: int,
        parent: QModelIndex | QPersistentModelIndex | None = None,
    ):
        """Insert `count` placeholder rows starting at `row`."""
        self.beginInsertRows(QModelIndex(), row, row + count - 1)
        self._get_list()[row:row] = [0] * count
        self.endInsertRows()
        self.layoutChanged.emit()
        return True

    def removeRows(
        self,
        row: int,
        count: int,
        parent: QModelIndex | QPersistentModelIndex | None = None,
    ):
        """Remove `count` rows starting at `row`."""
        self.beginRemoveRows(QModelIndex(), row, row + count - 1)
        del self._get_list()[row : row + count]
        self.endRemoveRows()
        self.layoutChanged.emit()
        return True

    def rowCount(
        self, parent: QModelIndex | QPersistentModelIndex = ...
    ) -> int:
        """Return the number of fields in this usage mode."""
        if self._project is None or self._project.pdata is None:
            return 0
        return len(self._get_list())

    def setData(
        self,
        index: QModelIndex | QPersistentModelIndex,
        value: Any,
        role=Qt.ItemDataRole.EditRole,
    ):
        """Set the field's column ID for a row inserted by a drop."""
        if role == Qt.ItemDataRole.EditRole:
            self._get_list()[index.row()] = value

        self.layoutChanged.emit()
        return True

    def setItemData(
        self, index: QModelIndex | QPersistentModelIndex, roles: dict[int, Any]
    ):
        """Set the field's column ID from the EditRole entry of `roles`."""
        if Qt.ItemDataRole.EditRole in roles:
            self._get_list()[index.row()] = roles[Qt.ItemDataRole.EditRole]
            return True
        else:
            return False
