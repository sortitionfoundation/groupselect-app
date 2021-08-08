from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QVariant, QModelIndex

from org.sortition.groupselect.data.TAAppData import TAAppData


class TAFieldsStringListModel(QtCore.QAbstractListModel):
    def __init__(self, fieldType: str, parent=None, *args):
        super(TAFieldsStringListModel, self).__init__(parent, *args)
        self.__currentAppData = TAAppData()
        self.__fieldType = fieldType

    def updateAppData(self, current_app_data: TAAppData):
        self.__currentAppData = current_app_data

    def __getStringList(self):
        return self.__currentAppData.fieldsUsage[self.__fieldType]

    def flags(self, index):
        if (not index.isValid() or index.row() >= self.rowCount(None) or index.model() != self):
            return Qt.ItemIsDropEnabled
        return super(TAFieldsStringListModel, self).flags(index) | Qt.ItemIsUserCheckable | Qt.ItemIsDragEnabled

    def supportedDropActions(self):
        return Qt.MoveAction

    def data(self, index, role):
        if not index.isValid():
            return None
        if index.row() > self.rowCount(None):
            return None

        j = self.__getStringList()[index.row()]
        if role == Qt.EditRole:
            return j
        elif role == Qt.DisplayRole:
            return self.__currentAppData.peopledata_keys[j] if j is not None else "(none)"

    def insertRows(self, row: int, count: int, parent=None):
        self.beginInsertRows(QModelIndex(), row, row+count-1)
        self.__getStringList()[row:row] = [0] * count
        self.endInsertRows()
        self.layoutChanged.emit()
        return True

    def removeRows(self, row: int, count: int, parent=None):
        self.beginRemoveRows(QModelIndex(), row, row+count-1)
        del self.__getStringList()[row:row+count]
        self.endRemoveRows()
        self.layoutChanged.emit()
        return True

    def rowCount(self, index):
        return len(self.__getStringList())

    def setData(self, index, value, role = Qt.EditRole):
        if role == Qt.ItemDataRole or role == Qt.EditRole:
            self.__getStringList()[index.row()] = value

        self.layoutChanged.emit()
        return True

    def setItemData(self, index, roles):
        if Qt.EditRole in roles:
            self.__getStringList()[index.row()] = roles[Qt.EditRole]
            return True
        else:
            return False

    def stringListUpdated(self):
        self.layoutChanged.emit()

    def supportedDropActions(self):
        return Qt.MoveAction