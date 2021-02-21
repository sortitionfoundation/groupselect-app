from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QTableView, QMenu, QAction


class TAPeopleDataTab(QTableView):
    def __init__(self, ctx):
        super(TAPeopleDataTab, self).__init__()
        self.ctx = ctx

        self.setModel(self.ctx.getPeopleDataModel())

        self.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.horizontalHeader().customContextMenuRequested.connect(self.__horizontalHeaderMenuPopup)

        self.verticalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.verticalHeader().customContextMenuRequested.connect(self.__verticalHeaderMenuPopup)

    def __horizontalHeaderMenuPopup(self, pos):
        menu = QMenu()
        actionRename = QAction('Rename', self)
        menu.addAction(actionRename)
        actionDelete = QAction('Delete', self)
        menu.addAction(actionDelete)

        action = menu.exec_(self.mapToGlobal(pos))

        col = self.columnAt(pos.x())

        if action == actionRename:
            self.__updateCatKey(col)
        elif action == actionDelete:
            # TODO: Implement
            print("delete col", col)
            raise Exception("Not implemented yet!")

    def __verticalHeaderMenuPopup(self, pos):
        menu = QMenu()
        actionDelete = QAction('Delete', self)
        menu.addAction(actionDelete)

        action = menu.exec_(self.mapToGlobal(pos))

        row = self.rowAt(pos.y())

        if action == actionDelete:
            # TODO: Implement
            print("delete row", row)
            raise Exception("Not implemented yet!")

    def __updateCatKey(self, j):
        old_key = self.model().getCatKey(j)
        new_key, ok = QInputDialog.getText(self, 'Change label for column %d' % j, 'New label for column:', QLineEdit.Normal, old_key)
        if not ok: return

        self.model().updateFieldName(j, new_key)
        self.ctx.changesToFile()