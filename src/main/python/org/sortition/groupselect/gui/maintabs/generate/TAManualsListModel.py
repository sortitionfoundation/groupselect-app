from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QVariant, QModelIndex

from org.sortition.groupselect.data.TAAppData import TAAppData


class TAManualsListModel(QtCore.QAbstractListModel):
    def __init__(self, app_data_manager: 'TAAppDataManager', parent=None, *args):
        super(TAManualsListModel, self).__init__(parent, *args)
        self.__currentAppData = TAAppData()
        self.__appDataManager = app_data_manager

    def updateAppData(self, current_app_data: TAAppData):
        self.__currentAppData = current_app_data

    def stringListUpdated(self):
        self.layoutChanged.emit()

    def data(self, index, role):
        if index.isValid() and index.row() <= self.rowCount(None) and role == Qt.DisplayRole:
            pid, gid = self.__getStringList()[index.row()]
            plabel = self.__appDataManager.get_print_labels(pid, include_pid = True)
            glabel = self.__appDataManager.get_group_label(gid)
            if not plabel: plabel = str(pid+1)
            if not glabel: plabel = str(gid+1)
            return "{0}: {1}".format(plabel, glabel)

        return None

    def rowCount(self, index):
        return len(self.__getStringList())

    def getSelectable(self):
        pidsSelectable = [pid for pid in range(len(self.__currentAppData.peopledata_vals)) if
                           pid not in [m[0] for m in self.__currentAppData.manuals]]
        pidsAndLabels = [(pid, self.__appDataManager.get_print_labels(pid)) for pid in pidsSelectable]

        return pidsAndLabels

    def getGroups(self):
        gids = list(range(self.__currentAppData.settings['numGroups']))
        groups = [(gid, self.__appDataManager.get_group_label(gid)) for gid in gids]

        return groups

    def addManual(self, pid, gid):
        self.__getStringList().append([pid, gid])
        self.layoutChanged.emit()

    def removeManual(self, index):
        del self.__getStringList()[index]
        self.layoutChanged.emit()

    def __getStringList(self):
        return self.__currentAppData.manuals