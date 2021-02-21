from PyQt5 import QtCore
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QTableView


class TAPeopleDataTab(QTableView):
    def __init__(self, ctx):
        super(TAPeopleDataTab, self).__init__()
        self.ctx = ctx

        self.__createUi()

    def __createUi(self):
        self.setModel(self.ctx.getPeopleDataModel())
        self.horizontalHeader().sectionDoubleClicked.connect(self.update_cat_key)

        # TODO: add cell changed trigger
        #self.table_widget.model().cellChanged.connect(self.ctx.set_unsaved)

    def update_cat_key(self, j):
        old_key = self.table_widget.model().getCatKey(j)
        new_key, ok = QInputDialog.getText(self, 'Change label for column %d' % j, 'New label for column:', QLineEdit.Normal, old_key)
        if not ok: return

        #self.table_widget.horizontalHeaderItem(j).setText(new_key)
        #self.ctx.app_data.peopledata_keys[j] = new_key
        self.model().updateFieldName(j, new_key)
        self.model().headerDataChanged.emit(QtCore.Qt.Horizontal, 0, 2)
        self.ctx.changesToFile()
        #self.ctx.window.tabs.peopledata_updated()