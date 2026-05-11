from typing import Sequence, Final

import csv
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



        total_row = self.row_count_participants()
        fields_display = self._fields_display()
        field_starts = total_row + 1
        field_end = field_starts + len(fields_display)
        custom_row = field_end

        self._participants = self._project.pdata_mapped.shape[0]

        total_col = len(self._allocation)
        groups = []
        for i in range(total_col):
            groups.append(self._allocation[i])

        complete = 0
        for i in range (len(groups)):
            fields_display = self._fields_display()
            row = self.row_count_participants() + 1
            field_id = fields_display[row - self.row_count_participants() - 1]
            value_counts = self._project.pdata_mapped[field_id].loc[groups[i]].value_counts()
            ideal_count = self._project.pdata_mapped[field_id].value_counts()
            deviation = [0] * 10
            j = 0
            for name, count in value_counts.items():
                ideal_dist = ideal_count[name] / self._participants
                table_count = ideal_dist * len(groups[i])
                table_dist = value_counts[name] / len(groups[i])
                deviation[j] = abs(table_dist - ideal_dist)
                j += 1
            total = 0
            for j in range(len(deviation)):
                total = total + deviation[j]
            ave = total/2

            complete = complete + ave
        self.total_ave = complete/len(groups)

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
        elif index.row() > self.row_count_participants() and index.row() < custom_row:
            if role == QtCore.Qt.ItemDataRole.DisplayRole:
                fields_display = self._fields_display()
                field_id = fields_display[index.row() - self.row_count_participants() - 1]
                field_name = self._project.data_handle.column_naming[field_id]
                value_counts = self._project.pdata_mapped[field_id].loc[group].value_counts()
                ideal_count = self._project.pdata_mapped[field_id].value_counts()
                deviation = [0] * 100
                i = 0
                for name, count in value_counts.items():
                    ideal_dist =  ideal_count[name] / self._participants
                    table_count = ideal_dist * len(group)
                    table_dist = value_counts[name] / len(group)
                    deviation[i] = abs(table_dist - ideal_dist)
                    i += 1
                    #print(ideal_count[name], table_count, deviation[i], self.row_count_participants(), "data")

                this = zip(value_counts.items(), deviation)
                return f"{field_name}:\n" + '\n'.join(
                    f"{term_count} {term_name} \n dev: {deviation}"
                    for (term_name, term_count), deviation in this
                )
        elif index.row() == custom_row:
            if role == QtCore.Qt.ItemDataRole.DisplayRole and index.column() == 0:


                i = 0
                #indexo = 0
                #for allos in self._project.results:

                 #   if allos == self._allocation:
                  #      indexo = i
                   # i += 1
                #print(indexo, "index")
                table_meets = [0] * 100
                self._meets = [[0] * (self._participants + 1) for _ in range((self._participants + 1))]

                self._dictmeets = {}

                for i in range (1, self._participants+1):
                    for j in range (i+1, self._participants+1):
                        self._dictmeets[(i, j)] = 0
                total_res = len(self._project.results)
                total_meets = (self._participants * (self._participants - 1) / 2)
                table_meets[0] = total_meets
                for alloc in self._project.results[total_res-10:total_res:]:
                    for table in alloc:
                     done = []
                     for id in table:
                      print(id, table)

                      done.append(id)
                      for p_id in table:
                        if p_id not in done:
                          a = min(id, p_id)
                          b = max(id, p_id)
                          self._dictmeets[(a,b)] += 1

                          #val = self._meets[a][b]
                          #self._meets[a][b] = val + 1
                          #table_meets[self._meets[a][b]-1] -= 1

                zero_meets = sum(1 for v in self._dictmeets.values() if v == 0)
                meets1 = sum(1 for v in self._dictmeets.values() if v == 1)
                meets2 = sum(1 for v in self._dictmeets.values() if v == 2)
                meets3 = sum(1 for v in self._dictmeets.values() if v == 3)
                meets4 = sum(1 for v in self._dictmeets.values() if v == 4)
                meets5 = sum(1 for v in self._dictmeets.values() if v == 5)
                meets6 = sum(1 for v in self._dictmeets.values() if v == 6)
                meets7 = sum(1 for v in self._dictmeets.values() if v == 7)
                meets8 = sum(1 for v in self._dictmeets.values() if v == 8)
                meets9 = sum(1 for v in self._dictmeets.values() if v == 9)

                meetval2 = meets1 + meets2/2 + meets3/3 + meets4/4 + meets5/5 + meets6/6 + meets7/7 + meets8/8 + meets9/9
                meetval2 = meetval2/len(self._dictmeets.values())

                non_zero_meets = 0
                #for i in range (1, 10):
                 #   print(table_meets[i], i)
                  #  non_zero_meets = non_zero_meets + table_meets[i]
                 #   if table_meets[i] == 0:
                   #     end = i
                    #    break


                #total_meets = (self._participants * (self._participants -1)/2)
                total_meets = len(self._dictmeets)
                #zero_meets = total_meets - non_zero_meets

                meet_val = zero_meets / total_meets

                print(total_meets, zero_meets, meet_val, meetval2, "final")




                new_row = [meet_val, meetval2]

                filename = "meetval(cons-12, weight-5).csv"
                with open(filename, 'a', newline='') as csvfile:

                    writer_obj = csv.writer(csvfile)
                    writer_obj.writerow(new_row)

                #with open(filename, 'w', newline='') as csvfile:
                 #   writer = csv.writer(csvfile)
                  #  writer.writerow(['meetval', 'meetval2'])
                   # writer.writerow([meet_val, meetval2])

                return ("\n Round Dist \n Deviation:\n" f"{self.total_ave}"
                        "\n Meeting Value:\n " f"{meet_val}")
                       # "\n Meeting Value2:\n" f"{meetval2}")

                return "\n".join(
                    f"{meet} pair(s) met {index} time"
                    for meet, index in zip(table_meets[1:end], range(1, end)))
                return table_meets[0:3]



    def row_count_participants(self):
        return max(len(group) for group in self._allocation)

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
          + 1
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
                elif index.row() > self.row_count_participants() and index.row() < custom_row:

                    if role == QtCore.Qt.ItemDataRole.DisplayRole:
                        fields_display = self._fields_display()
                        field_id = fields_display[index.row() - self.row_count_participants() - 1]
                        field_name = self._project.data_handle.column_naming[field_id]
                        value_counts = self._project.pdata_mapped[field_id].loc[group].value_counts()
                        return f"{field_name}:\n" + '\n'.join(
                            f"{term_count} {term_name}"
                            for term_name, term_count in value_counts.items()
                        )
                elif index.row() == custom_row:
                    if role == QtCore.Qt.ItemDataRole.DisplayRole:
                        return "plo"

            def row_count_participants(self):
                return max(len(group) for group in self._allocation)

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
                        + 1
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
                                return f"Group {index + 1}"
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

        # Return True, meaning that the drop event was processed.
        return True
