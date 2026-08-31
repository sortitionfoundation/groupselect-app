"""List model of the computed allocation results."""

from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from datahandling import excel_col_name

from base_app.AbstractProjectModel import AbstractProjectModel

from GSProject import GSProject


class GSResultsListModel(QtCore.QStringListModel, AbstractProjectModel):
    """List of the computed allocations, one entry per result."""

    _project: GSProject

    def __init__(self):
        """Initialise the model."""
        super(GSResultsListModel, self).__init__()

    # project updated
    def updated_project(self, project: GSProject):
        """Bind the model to a (newly opened) project."""
        self._project = project
        self.layoutChanged.emit()

    # Triggered when the project's results are updated.
    def updated_results(self):
        """Notify the view that the project's results changed."""
        self.layoutChanged.emit()

    def data(
        self,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
        role: int = ...,
    ):
        """Return the label for a result, or a placeholder if there is none."""
        if role == Qt.ItemDataRole.DisplayRole:
            if not self._project.results:
                return "No allocations"
            return f"Allocation {index.row() + 1}"
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            if not self._project.results:
                return Qt.AlignmentFlag.AlignCenter

    def rowCount(
        self, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex = ...
    ):
        """Return the number of results, or 1 for the placeholder entry."""
        if self._project is None:
            return 0

        return len(self._project.results) if self._project.results else 1

    def flags(self, index):
        """Return flags disabling selection when there are no results."""
        if not self._project.results:
            return Qt.ItemFlag.NoItemFlags

        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
