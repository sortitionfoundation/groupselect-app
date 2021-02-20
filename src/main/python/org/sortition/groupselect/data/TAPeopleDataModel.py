from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush

from org.sortition.groupselect.data.TAAppData import TAAppData


class TAPeopleDataModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None, *args):
        super(TAPeopleDataModel, self).__init__(parent, *args)
        self.__currentAppData = TAAppData()

    def updateAppData(self, current_app_data: TAAppData):
        self.__currentAppData = current_app_data
        self.layoutChanged.emit()

    def updateFieldName(self, j, newName):
        self.__currentAppData.peopledata_keys[j] = newName
        self.headerDataChanged.emit(QtCore.Qt.Horizontal, j, j)

    def data(self, index, role):
        if role == Qt.EditRole or role == Qt.DisplayRole:
            return self.__getDisplayData(index.row(), index.column(), ignoreTerms=(role==Qt.EditRole))
        if role == Qt.ForegroundRole:
            if self.__getDisplayData(index.row(), index.column()) != "(empty)":
                return QColor(Qt.black)
            else:
                return QColor(Qt.gray)
        if role == Qt.BackgroundRole:
            if self.__hasDataChangedByTerms(index.row(), index.column()):
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
            return QtCore.QVariant(col)

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.EditRole:
            return False

        self.__currentAppData.peopledata_vals[index.row()][index.column()] = value
        self.dataChanged.emit(index, index)

        return False

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def getCatKey(self, j):
        return self.__currentAppData.peopledata_keys[j]

    def __getDisplayData(self, i, j, ignoreTerms=False):
        r = self.__currentAppData.peopledata_vals[i][j]
        if ignoreTerms:
            return r
        elif not self.__currentAppData.peopledata_terms[j]:
            return r if r else "(empty)"
        else:
            try:
                return next(t_used if t_used else "(empty)" for t_found, t_used in self.__currentAppData.peopledata_terms[j] if t_found == r)
            except StopIteration:
                return r

    def __hasDataChangedByTerms(self, i, j):
        if not self.__currentAppData.peopledata_terms[j]: return False

        r = self.__currentAppData.peopledata_vals[i][j]

        try:
            if next(True for t_found, t_used in self.__currentAppData.peopledata_terms[j] if t_found == r and t_found != t_used):
                return True
        except StopIteration:
            return False