"""Table model for the currently selected allocation result, with drag-drop."""

from typing import Sequence, Final

import numpy as np
from PySide6 import QtCore
from PySide6.QtCore import (
    QModelIndex,
    QDataStream,
    QIODevice,
    QMimeData,
    QByteArray,
)

from groupselect import AllocationEnsemble

from GSAppFieldMode import GSAppFieldMode
from base_app.AbstractProjectModel import AbstractProjectModel

from GSProject import GSProject


MIME_TYPE_DRAG_DROP_ROWS_COLS: Final[str] = "application/x-gs-results-row-col"


class GSResultsTableModel(AbstractProjectModel, QtCore.QAbstractTableModel):
    """Table showing one allocation's groups as columns, with drag-drop."""

    _project: GSProject

    def __init__(self):
        """Initialise the model."""
        super(GSResultsTableModel, self).__init__()

    # Project updated.
    def updated_project(self, project: GSProject):
        """Bind the model to a (newly opened) project."""
        self._project = project
        self.layoutChanged.emit()

    # Results updated.
    def updated_results(self):
        """Notify the view that the project's results changed."""
        self.layoutChanged.emit()

    def update_current(
        self, setup_index: None | int, allocation_index: None | int
    ):
        """Switch to displaying the given setup's given allocation."""
        self._project.selected_setup = setup_index
        self._project.selected_allocation = allocation_index
        self.layoutChanged.emit()

    @property
    def _allocation(self) -> list[list]:
        """The currently selected allocation, or None if none is selected."""
        setup_index = self._project.selected_setup
        allocation_index = self._project.selected_allocation
        if setup_index is None or allocation_index is None:
            return None
        return self._project.setups[setup_index].ensemble[allocation_index]

    # abstract method implementations
    def data(self, index, role):
        """Return a participant's label, a group's stats, or overall stats."""
        if self._project is None or self._allocation is None:
            return None

        row_count_parts = self.row_count_participants()
        if index.column() == 0:
            if index.row() == row_count_parts + 1:
                total = sum(len(group) for group in self._allocation)
                ret = [f"Total size:\n{total}"]
                average_group_size = total / len(self._allocation)
                p_indexes = np.concatenate(self._allocation)
                per_term_factor = average_group_size / len(p_indexes)
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
                            f"{term_count * per_term_factor:.1f} {term_name}"
                            for (term_name, term_count) in value_counts.items()
                        )
                    )
                return "\n\n".join(ret)
            elif index.row() == row_count_parts + 2:
                # Only this one allocation's diversity score is shown here
                # -- the meeting score is an ensemble-wide metric (how well
                # *multiple* allocations complement each other) and isn't
                # meaningful for a single one; see the setup summary table
                # for that.
                people_data = self._project.pdata_mapped[
                    self._project.fields_display()
                ]
                diversity_score = AllocationEnsemble(
                    [self._allocation]
                ).calc_diversity_score(people_data)

                return f"\n\nDiversity:\n{diversity_score:.1f}"
        elif index.column() > 0:
            group = self._allocation[index.column() - 1]
            if index.row() < len(group):
                p_id = group[index.row()]
                p_index = self._project.pdata_mapped.index[p_id]
                if role == QtCore.Qt.ItemDataRole.DisplayRole:
                    fields_label = [
                        field_id
                        for (
                            field_usage,
                            field_ids,
                        ) in self._project.fields_usage.items()
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
        """Return the size of the largest group in the current allocation."""
        return max(len(group) for group in self._allocation)

    def rowCount(self, index):
        """Return the number of participant rows, plus 3 trailing rows."""
        if self._project is None or self._allocation is None:
            return 0

        # Total number of rows is number of rows for participants
        # plus one for drag-and-drop plus one for statistics plus
        # one for metrics.
        return self.row_count_participants() + 3

    def columnCount(self, index):
        """Return the number of groups, plus one label column."""
        if self._project is None or self._allocation is None:
            return 0

        return len(self._allocation) + 1

    def headerData(self, index, orientation, role):
        """Return the group's header label."""
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
        """Return flags enabling drag-and-drop between groups."""
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
        """Support only move actions, since drops reassign participants."""
        return QtCore.Qt.DropAction.MoveAction

    def mimeTypes(self):
        """Return the MIME type used to encode dragged cell positions."""
        return [MIME_TYPE_DRAG_DROP_ROWS_COLS]

    def mimeData(self, indexes: Sequence[QModelIndex]):
        """Encode a single dragged cell's row and column."""
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
        """Move the dragged participant to the drop target's group."""
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
