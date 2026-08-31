"""Tree model of the computed results: setups (ensembles) and allocations."""

from PySide6 import QtCore
from PySide6.QtCore import Qt, QModelIndex, QPersistentModelIndex

from base_app.AbstractProjectModel import AbstractProjectModel

from GSProject import GSProject


# Sentinel internalId marking a top-level (setup) index, so it can be told
# apart from an allocation index (whose internalId is its parent setup's
# row instead).
_TOP_LEVEL = 0xFFFFFFFF


class GSResultsTreeModel(QtCore.QAbstractItemModel, AbstractProjectModel):
    """Two-level tree: one row per setup, with its allocations as children."""

    _project: GSProject

    def __init__(self):
        """Initialise the model."""
        super(GSResultsTreeModel, self).__init__()

    # project updated
    def updated_project(self, project: GSProject):
        """Bind the model to a (newly opened) project."""
        self._project = project
        self.layoutChanged.emit()

    # Triggered when the project's setups/allocations are updated.
    def updated_results(self):
        """Notify the view that the project's results changed."""
        self.layoutChanged.emit()

    def node(
        self, index: QModelIndex | QPersistentModelIndex
    ) -> tuple[int, None | int]:
        """Return (setup_row, allocation_row); the latter None for a setup."""
        internal_id = index.internalId()
        if internal_id == _TOP_LEVEL:
            return index.row(), None
        return internal_id, index.row()

    def index_for_setup(self, setup_row: int) -> QModelIndex:
        """Return the index of the setup at the given row."""
        return self.createIndex(setup_row, 0, _TOP_LEVEL)

    def index_for_allocation(
        self, setup_row: int, allocation_row: int
    ) -> QModelIndex:
        """Return the index of the allocation at the given row of a setup."""
        return self.createIndex(allocation_row, 0, setup_row)

    def index(
        self,
        row: int,
        column: int,
        parent: QModelIndex | QPersistentModelIndex = QModelIndex(),
    ) -> QModelIndex:
        """Return the index for a row/column, either a setup or allocation."""
        if not parent.isValid():
            return self.createIndex(row, column, _TOP_LEVEL)
        return self.createIndex(row, column, parent.row())

    def parent(
        self, index: QModelIndex | QPersistentModelIndex = QModelIndex()
    ) -> QModelIndex:
        """Return the parent setup of an allocation, or an invalid index."""
        if not index.isValid():
            return QModelIndex()
        internal_id = index.internalId()
        if internal_id == _TOP_LEVEL:
            return QModelIndex()
        return self.createIndex(internal_id, 0, _TOP_LEVEL)

    def rowCount(
        self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()
    ) -> int:
        """Return the number of setups, or of allocations within a setup."""
        if self._project is None:
            return 0
        if not parent.isValid():
            return len(self._project.setups) if self._project.setups else 1
        setup_row, allocation_row = self.node(parent)
        if allocation_row is not None or parent.column() != 0:
            return 0
        if setup_row >= len(self._project.setups):
            return 0
        return len(self._project.setups[setup_row].ensemble)

    def columnCount(
        self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()
    ) -> int:
        """Return the (fixed) number of columns: one, holding the name."""
        return 1

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = ...,
    ):
        """Return the label for a setup or allocation, or a placeholder."""
        if not index.isValid():
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            if not self._project.setups:
                return "No setups yet"
            setup_row, allocation_row = self.node(index)
            if allocation_row is None:
                return self._project.setups[setup_row].name
            return self._project.setups[setup_row].allocation_names[
                allocation_row
            ]
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            if not self._project.setups:
                return Qt.AlignmentFlag.AlignCenter

    def flags(self, index: QModelIndex | QPersistentModelIndex):
        """Return flags disabling selection when there are no setups."""
        if not index.isValid() or not self._project.setups:
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
