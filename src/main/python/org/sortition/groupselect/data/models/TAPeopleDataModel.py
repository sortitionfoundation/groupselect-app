import copy

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui import QColor, QBrush

from org.sortition.groupselect.data.TAAppData import TAAppData


class TAPeopleDataModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None, *args):
        super(TAPeopleDataModel, self).__init__(parent, *args)
        self.__currentAppData = TAAppData()

        self.__viewState = True

    # update appData object
    def updateAppData(self, current_app_data: TAAppData):
        self.__currentAppData = current_app_data
        self.layoutChanged.emit()

    # change settings for field view
    def setFieldsView(self, view_state):
        self.__viewState = view_state
        self.layoutChanged.emit()

    # abstract method implementations
    def data(self, index, role):
        if role == Qt.EditRole or role == Qt.DisplayRole:
            return self.__getDisplayData(index.row(), index.column(),
                                         ignoreTerms=(role == Qt.EditRole or not self.__viewState))
        if role == Qt.ForegroundRole:
            if not self.__viewState or self.__getDisplayData(index.row(), index.column()) != "(empty)":
                return QColor(Qt.black)
            else:
                return QColor(Qt.gray)
        if role == Qt.BackgroundRole:
            if self.__viewState and self.__hasDataChangedByTerms(index.row(), index.column()):
                brush = QBrush(Qt.BDiagPattern)
                brush.setColor(Qt.lightGray)
                return brush
            else:
                return QColor(Qt.white)

    def rowCount(self, index):
        return len(self.__currentAppData.peopledata_vals)

    def columnCount(self, index):
        return len(self.__currentAppData.peopledata_vals[0]) if self.__currentAppData.peopledata_vals else 0

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.__currentAppData.peopledata_keys[col])
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(col + 1)

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.EditRole:
            return False

        self.__currentAppData.peopledata_vals[index.row()][index.column()] = value
        self.dataChanged.emit(index, index)

        return False

    def getKeys(self):
        return self.__currentAppData.peopledata_keys

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def __getDisplayData(self, i, j, ignoreTerms=False):
        r = self.__currentAppData.peopledata_vals[i][j]
        if ignoreTerms:
            return r
        elif not self.__currentAppData.peopledata_terms[j]:
            return r if r else "(empty)"
        else:
            try:
                return next(
                    t_used if t_used else "(empty)" for t_found, t_used in self.__currentAppData.peopledata_terms[j] if
                    t_found == r)
            except StopIteration:
                return r

    def __hasDataChangedByTerms(self, i, j):
        if not self.__currentAppData.peopledata_terms[j]: return False

        r = self.__currentAppData.peopledata_vals[i][j]

        try:
            if next(True for t_found, t_used in self.__currentAppData.peopledata_terms[j] if
                    t_found == r and t_found != t_used):
                return True
        except StopIteration:
            return False

    # externally invoked data updates
    def generateNewData(self, number: int, names: str):
        m_data = number
        n_data = len(names.split(","))

        keys = [n.strip() for n in names.split(",")]
        vals = [['' for j in range(n_data)] for i in range(m_data)]
        terms = [None for j in range(n_data)]

        self.__updateData(keys, vals, terms)

    def insertFromImport(self, keys, vals):
        terms = len(keys) * [None]

        self.__updateData(keys, vals, terms)

    def updateFromImport(self, keys, vals, consider_sources: bool = False):
        terms = copy.deepcopy(self.__currentAppData.peopledata_terms)

        if len(keys) > len(terms):
            terms.extend((len(keys) - len(terms)) * [None])
        elif len(keys) < len(terms):
            terms = terms[:len(keys)]

        self.__updateData(keys, vals, terms, consider_sources)

    def __updateData(self, keys: list, vals: list, terms: list, consider_sources: bool = False):
        rows = self.rowCount(0)
        cols = self.columnCount(0)

        self.beginInsertRows(QModelIndex(), 0, rows)
        self.beginInsertColumns(QModelIndex(), 0, cols)

        if not consider_sources:
            self.__currentAppData.peopledata_keys = keys
            self.__currentAppData.peopledata_vals = vals

            self.__currentAppData.peopledata_keys_sources = {i: i for i in range(len(keys))}
        else:
            nCols = len(self.__currentAppData.peopledata_keys)
            lenOld = len(self.__currentAppData.peopledata_vals)
            lenNew = len(vals)

            for i in range(lenNew-lenOld):
                self.__currentAppData.peopledata_vals.append(nCols * [''])

            # if lenOld < lenNew:
            #     for i in range(lenNew-lenOld):
            #        self.__currentAppData.peopledata_vals.append(nCols * [''])
            # else:
            #     self.__currentAppData.peopledata_vals = self.__currentAppData.peopledata_vals[0:lenNew]

            for col in self.__currentAppData.peopledata_keys:
                if col not in self.__currentAppData.peopledata_keys_sources:
                    continue

                j1 = self.__currentAppData.peopledata_keys.index(col)
                j2 = keys.index(self.__currentAppData.peopledata_keys_sources[col])
                for i in range(lenNew):
                    self.__currentAppData.peopledata_vals[i][j1] = vals[i][j2]

            self.__currentAppData.peopledata_vals = vals
        self.__currentAppData.peopledata_terms = terms

        self.endInsertColumns()
        self.endInsertRows()

        self.layoutChanged.emit()

    def updateFieldName(self, j, new_name):
        self.__currentAppData.peopledata_keys[j] = new_name
        self.headerDataChanged.emit(QtCore.Qt.Horizontal, j, j)

    # public getter methods
    def isEmpty(self):
        return not any(self.__currentAppData.peopledata_vals[i][j] for j in range(self.columnCount(None)) for i in
                       range(self.rowCount(None)))

    def getCatKey(self, j):
        return self.__currentAppData.peopledata_keys[j]
