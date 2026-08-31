"""Table model exposing the project's allocation settings as a single row."""

from typing import Any

from PySide6 import QtCore
from PySide6.QtCore import Qt, QModelIndex, QPersistentModelIndex

from base_app.AbstractProjectModel import AbstractProjectModel
from GSProject import GSProject, settings_lookup, settings_template


class GSAllocationSettingsModel(
    QtCore.QAbstractTableModel, AbstractProjectModel
):
    """Single-row table model with one column per allocation setting."""

    _project: GSProject

    # project updated
    def updated_project(self, project: GSProject):
        """Bind the model to a (newly opened) project."""
        self._project = project
        self.dataChanged.emit(
            self.createIndex(0, 0), self.createIndex(0, len(settings_lookup))
        )

    def data(
        self, index: QModelIndex | QPersistentModelIndex, role: int = ...
    ):
        """Return the setting value for the given column."""
        if self._project is None:
            return 0
        if role in [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole]:
            key = settings_lookup[index.column()]
            return self._project.settings[key]
        return None

    def rowCount(
        self, parent: QModelIndex | QPersistentModelIndex = ...
    ) -> int:
        """Return 1, as all settings live in a single row."""
        return 1

    def columnCount(
        self, parent: QModelIndex | QPersistentModelIndex = ...
    ) -> int:
        """Return the number of allocation settings."""
        return len(settings_lookup)

    def setData(
        self,
        index: QModelIndex | QPersistentModelIndex,
        value: Any,
        role=QtCore.Qt.ItemDataRole.DisplayRole,
    ):
        """Store an edited setting value, coercing to its template type."""
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
        """Return the value of a single setting by key."""
        return self._project.settings.get(key, __default=None)

    def set_setting(self, key: str, value: Any):
        """Set the value of a single setting by key and notify the view."""
        self._project.settings[key] = value
        column = settings_lookup.index(key)
        self.dataChanged.emit(
            self.createIndex(0, column), self.createIndex(0, column)
        )
