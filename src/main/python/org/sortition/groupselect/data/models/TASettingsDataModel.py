from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtWidgets import QMessageBox

from org.sortition.groupselect.data.TAAppData import TAAppData


class TASettingsDataModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None, *args):
        super(TASettingsDataModel, self).__init__(parent, *args)
        self.__currentAppData = TAAppData()

    def updateAppData(self, current_app_data: TAAppData):
        self.__currentAppData = current_app_data
        self.layoutChanged.emit()

    def data(self, index, role):
        if role == Qt.EditRole or role == Qt.DisplayRole:
            key = list(self.__currentAppData.settings.keys())[index.column()]
            return self.__currentAppData.settings[key]

    def rowCount(self, index):
        return 1

    def columnCount(self, index):
        return len(self.__currentAppData.settings)

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.EditRole:
            return False

        key = list(self.__currentAppData.settings.keys())[index.column()]

        try:
            self.__currentAppData.settings[key] = int(value)
        except ValueError as e:
            QMessageBox.critical(None, "Error", "Error occurred while processing your entry:\n\n{}".format(str(e)))
            return True

        self.dataChanged.emit(index, index)

        return False