from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from org.sortition.groupselect.data.TAAppData import TAAppData


class TAColmapDataModel(QtCore.QAbstractTableModel):
    def __init__(self, keys: list, old_keys: list, colmap: list, parent=None, *args):
        super(TAColmapDataModel, self).__init__(parent, *args)
        self.__keys = keys
        self.__oldKeys = old_keys
        self.__colmap = len(keys) * [None]

        if colmap:
            for colSrc, colTarget in enumerate(colmap[0:len(keys)]):
                self.__colmap[colSrc] = colTarget

    def getColmap(self):
        return self.__colmap

    # abstract method implementations
    def data(self, index, role):
        if role not in [Qt.DisplayRole, Qt.EditRole]:
            return

        if index.column() == 0:
            r = self.__keys[index.row()]
        else:
            cm = self.__colmap[index.row()]
            if role == Qt.DisplayRole:
                r = f"Update column {self.__oldKeys[cm]}" if isinstance(cm, int) else\
                    'Create new column' if cm == 'new' else\
                    'Ignore'
            elif role == Qt.EditRole:
                r = cm

        return QtCore.QVariant(r)

    def rowCount(self, index):
        return len(self.__keys)

    def columnCount(self, index):
        return 2

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if col == 0:
                return QtCore.QVariant('Imported columns')
            else:
                return QtCore.QVariant('Existing columns')

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.EditRole or index.column() != 1:
            return False

        self.__colmap[index.row()] = value

        return False

    def flags(self, index):
        if index.column() == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable