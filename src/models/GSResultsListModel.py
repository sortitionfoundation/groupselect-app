from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from datahandling import excel_col_name

from AbstractProjectModel import AbstractProjectModel

from src.GSProject import GSProject


class GSResultsListModel(QtCore.QStringListModel, AbstractProjectModel):
    _project: GSProject

    def __init__(self):
        super(GSResultsListModel, self).__init__()

    # project updated
    def updated_project(self, project: GSProject):
        self._project = project
        self.layoutChanged.emit()

    # Triggered when the project's results are updated.
    def updated_results(self):
        self.layoutChanged.emit()

    def data(self, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex, role: int = ...):
        if role == Qt.ItemDataRole.DisplayRole:
            if not self._project.results:
                return 'No allocations'
            return f"Allocation {index.row() + 1}"
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            if not self._project.results:
                return Qt.AlignmentFlag.AlignCenter

    def rowCount(self, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex = ...):
        if self._project is None:
            return 0

        return len(self._project.results) if self._project.results else 1

    def flags(self, index):
        if not self._project.results:
            return Qt.ItemFlag.NoItemFlags

        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
