from typing import Final, Sequence

import numpy as np
from base_app.AbstractProjectModel import AbstractProjectModel
from GSAppFieldMode import GSAppFieldMode
from GSProject import GSProject
from PySide6 import QtCore
from PySide6.QtCore import (
    QByteArray,
    QDataStream,
    QIODevice,
    QMimeData,
    QModelIndex,
)

MIME_TYPE_DRAG_DROP_ROWS_COLS: Final[str] = "application/x-gs-results-row-col"


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
            if self._project.result_current is None
            else self._project.results[self._project.result_current]
        )

    # abstract method implementations
    def data(self, index, role):
        if self._project is None or self._allocation is None:
            return None

        row_count_parts = self.row_count_participants()
        if index.column() == 0:
            if index.row() == row_count_parts + 1:
                total = sum(len(group) for group in self._allocation)
                ret = [f"Total size:\n{total}"]
                average_group_size = total / len(self._allocation)
                p_indexes = np.concatenate(self._allocation)
                denominator = len(p_indexes) / average_group_size
                for field_id in self._project.fields_display():
                    field_name = self._project.data_handle.column_naming[
                        field_id
                    ]
                    value_counts = (
                        self._project.pdata_mapped[field_id]
                        .iloc[p_indexes]
                        .value_counts()
                    )

                    ret.append(
                        f"{field_name}:\n"
                        + "\n".join(
                            f"{term_count / denominator:.1f} {term_name}"
                            for (term_name, term_count) in value_counts.items()
                        )
                    )
                return "\n\n".join(ret)
            elif index.row() == row_count_parts + 2:
                people_data = self._project.pdata_mapped[
                    self._project.fields_display()
                ]
                diversity_score = self._project.results.calc_diversity_score(
                    people_data
                )
                meeting_score = self._project.results.calc_meeting_norm_score()

                return (
                    "\n\n"
                    f"Diversity:\n{diversity_score:.1f}\n"
                    f"Meetings:\n{meeting_score:.1%}"
                )
        elif index.column() > 0:
            group = self._allocation[index.column() - 1]
            if index.row() < len(group):
                p_id = group[index.row()]
                p_index = self._project.pdata_mapped.index[p_id]
                fields_usage = self._project.fields_usage
                if role == QtCore.Qt.ItemDataRole.DisplayRole:
                    fields_label = [
                        field_id
                        for field_usage, field_ids in fields_usage.items()
                        for field_id in field_ids
                        if field_usage == GSAppFieldMode.Label
                    ]
                    if fields_label:
                        return (
                            " ".join(
                                self._project.pdata_mapped.loc[
                                    p_index, fields_label
                                ]
                            )
                            + f" ({p_index})"
                        )
                    else:
                        return str(p_index)
                elif role == QtCore.Qt.ItemDataRole.ToolTipRole:
                    fields_display = self._project.fields_display()
                    p_display = (
                        self._project.pdata_mapped.filter(fields_display)
                        .rename(
                            columns=self._project.data_handle.column_naming
                        )
                        .loc[p_index]
                    )
                    return "\n".join(
                        f"{field_key}: {field_val}"
                        for field_key, field_val in p_display.items()
                    )
            elif index.row() == row_count_parts + 1:
                if role == QtCore.Qt.ItemDataRole.DisplayRole:
                    ret = [f"Group size:\n{len(group)}"]
                    for field_id in self._project.fields_display():
                        field_name = self._project.data_handle.column_naming[
                            field_id
                        ]
                        value_counts = (
                            self._project.pdata_mapped[field_id]
                            .iloc[group]
                            .value_counts()
                            .reindex(
                                self._project.pdata_mapped[field_id].unique(),
                                fill_value=0,
                            )
                        )

                        ret.append(
                            f"{field_name}:\n"
                            + "\n".join(
                                f"{term_count} {term_name}"
                                for (
                                    term_name,
                                    term_count,
                                ) in value_counts.items()
                            )
                        )

                    return "\n\n".join(ret)

    def row_count_participants(self):
        return max(len(group) for group in self._allocation)

    def rowCount(self, index):
        if self._project is None or self._allocation is None:
            return 0

        # Total number of rows is number of rows for participants
        # plus one for drag-and-drop plus one for statistics plus
        # one for metrics.
        return self.row_count_participants() + 3

    def columnCount(self, index):
        if self._project is None or self._allocation is None:
            return 0

        return len(self._allocation) + 1

    def headerData(self, index, orientation, role):
        if self._project is None or self._allocation is None:
            return None

        match role:
            case QtCore.Qt.ItemDataRole.DisplayRole:
                match orientation:
                    case QtCore.Qt.Orientation.Horizontal:
                        return f"Group {index}" if index else ""
                    case QtCore.Qt.Orientation.Vertical:
                        return ""
                    case _:
                        raise Exception(f"Unknown orientation: {orientation}")
            case _:
                return None

    def flags(self, index):
        default_flags = super(GSResultsTableModel, self).flags(index)

        if not index.isValid():
            return QtCore.Qt.ItemFlag.NoItemFlags

        row_count_parts = self.row_count_participants()

        if index.row() > row_count_parts:
            return QtCore.Qt.ItemFlag.ItemIsEnabled

        if index.column() == 0:
            return QtCore.Qt.ItemFlag.NoItemFlags

        elif index.row() == len(self._allocation[index.column() - 1]):
            return QtCore.Qt.ItemFlag.ItemIsDropEnabled | default_flags
        else:
            return (
                QtCore.Qt.ItemFlag.ItemIsDragEnabled
                | QtCore.Qt.ItemFlag.ItemIsDropEnabled
                | default_flags
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
        row_old, col_old = bytereader.readInt64(), bytereader.readInt64() - 1

        # Get row and column of target cell.
        row_new, col_new = (
            (row, column - 1)
            if (row >= 0 and column >= 0)
            else (parent.row(), parent.column() - 1)
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
