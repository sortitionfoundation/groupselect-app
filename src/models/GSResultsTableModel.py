from typing import Sequence, Final

import numpy as np
from PySide6 import QtCore
from PySide6.QtCore import QModelIndex, QDataStream, QIODevice, QMimeData, QByteArray

from GSAppFieldMode import GSAppFieldMode
from base_app.AbstractProjectModel import AbstractProjectModel

from GSProject import GSProject


MIME_TYPE_DRAG_DROP_ROWS_COLS: Final[str] = 'application/x-gs-results-row-col'


class GSResultsTableModel(AbstractProjectModel, QtCore.QAbstractTableModel):
    _project: GSProject

    def __init__(self):
        super(GSResultsTableModel, self).__init__()

    # Project updated.
    def updated_project(self, project: GSProject):
        self._project = project
        self.layoutChanged.emit()

    # Results updated.
    def updated_results(self):
        self.layoutChanged.emit()

    def update_current(self, index: QModelIndex):
        self._project.result_current = index.row()
        self.layoutChanged.emit()

    @property
    def _allocation(self) -> list[list]:
        return (
            None
            if self._project.result_current is None else
            self._project.results[self._project.result_current]
        )

    def _fields_display(self):
        return [
            field_id
            for field_usage, field_ids in self._project.fields_usage.items()
            for field_id in field_ids
            if field_usage in [GSAppFieldMode.Diversify,
                               GSAppFieldMode.Cluster,
                               GSAppFieldMode.Display]
        ]

    # abstract method implementations
    def data(self, index, role):
        if self._project is None or self._allocation is None:
            return None

        group = self._allocation[index.column()]
        if index.row() < len(group):
            p_id = group[index.row()]
            if role == QtCore.Qt.ItemDataRole.DisplayRole:
                fields_label = [
                    field_id
                    for field_usage, field_ids in self._project.fields_usage.items()
                    for field_id in field_ids
                    if field_usage == GSAppFieldMode.Label
                ]
                if fields_label:
                    return ' '.join(self._project.pdata_mapped.loc[p_id, fields_label]) + f" ({p_id})"
                else:
                    return str(p_id)
            elif role == QtCore.Qt.ItemDataRole.ToolTipRole:
                fields_display = self._fields_display()
                p_display = (
                    self._project.pdata_mapped
                    .filter(fields_display)
                    .rename(columns=self._project.data_handle.column_naming)
                    .loc[p_id]
                )
                return "\n".join(
                    f"{field_key}: {field_val}"
                    for field_key, field_val in p_display.items()
                )
        elif index.row() == self.row_count_participants():
            if role == QtCore.Qt.ItemDataRole.DisplayRole:
                return f"Total: {len(group)}"
        elif index.row() > self.row_count_participants():
            if role == QtCore.Qt.ItemDataRole.DisplayRole:
                fields_display = self._fields_display()
                field_id = fields_display[index.row() - self.row_count_participants() - 1]
                field_name = self._project.data_handle.column_naming[field_id]
                value_counts = self._project.pdata_mapped[field_id].loc[group].value_counts()
                return f"{field_name}:\n" + '\n'.join(
                    f"{term_count} {term_name}"
                    for term_name, term_count in value_counts.items()
                )

    def row_count_participants(self):
        return max(len(group) for group in self._allocation) + 1

    def rowCount(self, index):
        if self._project is None or self._allocation is None:
            return 0

        fields_display = self._fields_display()

        # Total number of rows is number of rows for participants
        # plus one for total plus one row per field
        return (
            self.row_count_participants()
          + 1
          + len(fields_display)
        )

    def columnCount(self, index):
        if self._project is None or self._allocation is None:
            return 0

        return len(self._allocation)

    def headerData(self, index, orientation, role):
        if self._project is None or self._allocation is None:
            return None

        match role:
            case QtCore.Qt.ItemDataRole.DisplayRole:
                match orientation:
                    case QtCore.Qt.Orientation.Horizontal:
                        return f"Group {index+1}"
                    case QtCore.Qt.Orientation.Vertical:
                        return ''
                    case _:
                        raise Exception(f"Unknown orientation: {orientation}")
            case _:
                return None

    def flags(self, index):
        default_flags = super(GSResultsTableModel, self).flags(index)

        if not index.isValid() or index.row() > len(self._allocation[index.column()]):
            return QtCore.Qt.ItemFlag.NoItemFlags
        elif index.row() == len(self._allocation[index.column()]):
            return (
                QtCore.Qt.ItemFlag.ItemIsDropEnabled |
                default_flags
            )
        else:
            return (
                QtCore.Qt.ItemFlag.ItemIsDragEnabled |
                QtCore.Qt.ItemFlag.ItemIsDropEnabled |
                default_flags
            )

    def supportedDropActions(self):
        return QtCore.Qt.DropAction.MoveAction

    def mimeTypes(self):
        return [MIME_TYPE_DRAG_DROP_ROWS_COLS]

    def mimeData(self, indexes: Sequence[QModelIndex]):
        if len(indexes) > 1:
            return None
        index = indexes[0]

        bytearray = QByteArray()
        bytewriter = QDataStream(bytearray, QIODevice.WriteOnly)
        bytewriter.writeInt64(index.row())
        bytewriter.writeInt64(index.column())
        data = QMimeData()
        data.setData(MIME_TYPE_DRAG_DROP_ROWS_COLS, bytearray)

        return data

    def dropMimeData(self, data, action, row, column, parent):
        if MIME_TYPE_DRAG_DROP_ROWS_COLS not in data.formats():
            return False

        # Get row and column of cell that was dragged.
        bytearray = data.data(MIME_TYPE_DRAG_DROP_ROWS_COLS)
        bytereader = QDataStream(bytearray, QIODevice.ReadOnly)
        row_old, col_old = bytereader.readInt64(), bytereader.readInt64()

        # Get row and column of target cell.
        row_new, col_new = (
            (row, column)
            if (row >= 0 and column >= 0) else
            (parent.row(), parent.column())
        )

        # Update allocation.
        allocation = self._allocation
        p_id = allocation[col_old][row_old]
        del allocation[col_old][row_old]
        if row_new < len(allocation[col_new]):
            allocation[col_new].insert(row_new, p_id)
        else:
            allocation[col_new].append(p_id)

        # Emit layout changed so that the table gets updated.
        self.layoutChanged.emit()

        # Return True, meaning that the drop event was processed.
        return True
