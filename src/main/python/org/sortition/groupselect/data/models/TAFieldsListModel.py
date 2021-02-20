from PyQt5 import QtCore
from PyQt5.QtCore import Qt

from org.sortition.groupselect.data.TAAppData import TAAppData


class TAFieldsListModel(QtCore.QStringListModel):
    def __init__(self, parent=None, *args):
        super(TAFieldsListModel, self).__init__(parent, *args)
        self.__currentAppData = TAAppData()

    def updateAppData(self, current_app_data: TAAppData):
        self.__currentAppData = current_app_data
        self.layoutChanged.emit()

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.__currentAppData.peopledata_keys[index.row()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self.__currentAppData.peopledata_keys)

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable