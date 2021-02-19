from PyQt5 import QtCore
from PyQt5.QtCore import Qt

from org.sortition.groupselect.data.TAAppData import TAAppData


class TAPeopleDataModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None, *args):
        super(TAPeopleDataModel, self).__init__(parent, *args)
        self.__currentAppData = TAAppData()

    def updateAppData(self, current_app_data: TAAppData):
        self.__currentAppData = current_app_data
        self.layoutChanged.emit()

    def data(self, index, role):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return self.__currentAppData.peopledata_vals[index.row()][index.column()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self.__currentAppData.peopledata_vals)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self.__currentAppData.peopledata_vals[0]) if self.__currentAppData.peopledata_vals else 0

    def headerData(self, col, orientation, role):
        #if orientation == QtCore.Qt.Horizontal: print(role)
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

    def updateFieldName(self, j, newName):
        self.__currentAppData.peopledata_keys[j] = newName
        self.headerDataChanged.emit(QtCore.Qt.Horizontal, j, j)

    def getCatKey(self, j):
        return self.__currentAppData.peopledata_keys[j]

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable