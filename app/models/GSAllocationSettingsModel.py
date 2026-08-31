from typing import Any

from PySide6 import QtCore
from PySide6.QtCore import Qt, QModelIndex, QPersistentModelIndex

from base_app.AbstractProjectModel import AbstractProjectModel
from GSProject import GSProject, settings_lookup, settings_template


class GSAllocationSettingsModel(QtCore.QAbstractTableModel, AbstractProjectModel):
    _project: GSProject

    # project updated
    def updated_project(self, project: GSProject):
        self._project = project
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(0, len(settings_lookup)))

    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = ...):
        if self._project is None:
            return 0
        if role in [Qt.ItemDataRole.DisplayRole,
                    Qt.ItemDataRole.EditRole]:
            key = settings_lookup[index.column()]
            return self._project.settings[key]
        return None

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = ...) -> int:
        return 1

    def columnCount(self, parent: QModelIndex | QPersistentModelIndex = ...) -> int:
        return len(settings_lookup)

    def setData(self, index: QModelIndex | QPersistentModelIndex, value: Any, role=QtCore.Qt.ItemDataRole.DisplayRole):
        # Don't do anything if no project has been defined.
        if self._project is None:
            return False

        # Ensure that the role is the EditRole.
        if role != QtCore.Qt.ItemDataRole.EditRole:
            return False

        # Get the key from the column index.
        key = settings_lookup[index.column()]

        # Set value in project settings dict.
        if isinstance(settings_template[key], int):
            value = int(value)
        elif isinstance(settings_template[key], float):
            value = float(value)
        self._project.settings[key] = value

        # Emit dataChanged signal.
        self.dataChanged.emit(index, index)

        return False

    def get_setting(self, key: str) -> Any:
        return self._project.settings.get(key, __default=None)

    def set_setting(self, key: str, value: Any):
        self._project.settings[key] = value
        column = settings_lookup.index(key)
        self.dataChanged.emit(self.createIndex(0, column), self.createIndex(0, column))
