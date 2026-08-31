"""Table model backing the import preview, with per-column naming and use."""

import copy

from typing import TYPE_CHECKING

import pandas as pd
from PySide6 import QtCore, QtGui

from datahandling import excel_col_name

if TYPE_CHECKING:
    from .GSPreviewDialog import GSPreviewDialog


class GSPreviewTableModel(QtCore.QAbstractTableModel):
    """Table model showing preview rows, delegating state to the dialog."""

    def __init__(self, dialog: "GSPreviewDialog"):
        """Initialise the model, keeping a reference to the owning dialog."""
        super(GSPreviewTableModel, self).__init__(dialog)

        self._dialog: "GSPreviewDialog" = dialog

    @property
    def _data(self) -> pd.DataFrame:
        return self._dialog.data

    @property
    def _file_config(self) -> dict:
        return self._dialog.file_config

    @property
    def _column_naming(self) -> dict[int, None | str]:
        return self._dialog.column_naming

    # abstract method implementations
    def data(
        self,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
        role: int = ...,
    ):
        """Return the cell text, or its highlight colours for used rows."""
        row_id, col_id = self._get_indices(index)

        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            cell = self._data.loc[row_id].iloc[col_id]
            return str(cell) if cell == cell else ""
        elif (role == QtCore.Qt.ItemDataRole.ForegroundRole) or (
            role == QtCore.Qt.ItemDataRole.BackgroundRole
        ):
            if (
                self._file_config["first"]
                <= row_id
                <= self._file_config["last"]
                and col_id in self._column_naming
            ):
                return (
                    QtGui.QColor(QtCore.Qt.GlobalColor.black)
                    if (role == QtCore.Qt.ItemDataRole.ForegroundRole)
                    else QtGui.QColor(QtCore.Qt.GlobalColor.white)
                )
            else:
                return (
                    QtGui.QColor(128, 128, 128)
                    if (role == QtCore.Qt.ItemDataRole.ForegroundRole)
                    else QtGui.QColor(239, 239, 239)
                )

    def rowCount(
        self, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex = ...
    ):
        """Return the number of preview rows."""
        return len(self._data)

    def columnCount(
        self, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex = ...
    ):
        """Return the number of preview columns."""
        return len(self._data.columns)

    def headerData(
        self, section: int, orientation: QtCore.Qt.Orientation, role: int = ...
    ):
        """Return the spreadsheet-style column header or the row number."""
        if (
            orientation == QtCore.Qt.Orientation.Horizontal
            and role == QtCore.Qt.ItemDataRole.DisplayRole
        ):
            col_id = section
            col_name = excel_col_name(col_id)
            return (
                f"{col_name} ({self._column_naming[col_id]})"
                if col_id in self._column_naming
                and self._column_naming[col_id] is not None
                else col_name
            )
        if (
            orientation == QtCore.Qt.Orientation.Vertical
            and role == QtCore.Qt.ItemDataRole.DisplayRole
        ):
            row_id = section
            return self._data.index[row_id]

    def flags(self, index):
        """Return the flags marking cells as enabled and selectable."""
        return (
            QtCore.Qt.ItemFlag.ItemIsEnabled
            | QtCore.Qt.ItemFlag.ItemIsSelectable
        )

    def _get_indices(self, index):
        return index.row() + 1, index.column()

    def get_column_name(self, col_id: int) -> str:
        """Return the assigned name for a column, or its spreadsheet letter."""
        return (
            self._column_naming[col_id]
            if col_id in self._column_naming
            else excel_col_name(col_id)
        )

    def set_column_name(self, col_id: int, col_name: str):
        """Set the name assigned to a column and notify the view."""
        column_naming_new = copy.deepcopy(self._column_naming)

        # set new usage
        column_naming_new[col_id] = col_name

        # update usage
        self._dialog.column_naming = column_naming_new

        # emit header data changed signal
        self.headerDataChanged.emit(
            QtCore.Qt.Orientation.Horizontal, 0, self.columnCount()
        )

    def auto_detect_column_names(self, row_id_headings: int):
        """Fill in column names by reading them from a given row."""
        # check that row_id_headings is within bounds
        if row_id_headings < 1 or row_id_headings > len(self._data):
            return

        # auto detect column names from
        self._dialog.column_naming |= (
            self._data.loc[row_id_headings]
            .iloc[list(self._dialog.column_naming.keys())]
            .dropna()
            .drop_duplicates()
            .to_dict()
        )

        # emit header data changed signal
        self.headerDataChanged.emit(
            QtCore.Qt.Orientation.Horizontal, 0, self.columnCount()
        )

    def get_column_use(self, col_id: int) -> bool:
        """Return whether a column is currently marked for import."""
        return col_id in self._column_naming

    def set_column_use(self, col_id: int, col_use: bool):
        """Mark a column as used or unused for import."""
        if col_use:
            if col_id not in self._column_naming:
                self._column_naming[col_id] = None
        else:
            del self._column_naming[col_id]
