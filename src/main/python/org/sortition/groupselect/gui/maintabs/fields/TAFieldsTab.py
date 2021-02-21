from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QListWidgetItem, QHeaderView, QHBoxLayout, QListView, QTableView


class TAFieldsTab(QWidget):
    def __init__(self, ctx):
        super(TAFieldsTab, self).__init__()
        self.ctx = ctx

        self.createUi()

    def createUi(self):
        self.fields_list = QListView()
        self.fields_list.setModel(self.ctx.getFieldsListModel())
        self.fields_list.selectionModel().currentChanged.connect(self.fieldlist_select)

        self.terms_table = QTableView()
        self.terms_table.setModel(self.ctx.getTermsDataModel())
        #self.terms_table.setHorizontalHeaderLabels(['Terms Found', 'Terms Usage'])
        self.terms_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.terms_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        #self.terms_table.cellChanged.connect(self.userchanged_table)

        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.fields_list)
        layout.addWidget(self.terms_table)
        self.setLayout(layout)

        self.fieldlist_disable()

    def fieldlist_enable(self):
        self.terms_table.setDisabled(False)

    def fieldlist_disable(self):
        self.terms_table.setDisabled(True)

    def fieldlist_select(self, current):
        self.fieldlist_enable()
        self.terms_table.model().updateKey(current.row())

    def display_none(self):
        self.fields_list.clearSelection()
        self.status_mode_box(False)
        self.status_terms_group(False)

    def get_current_field_index(self):
        return self.fields_list.currentItem().data(Qt.UserRole)

    def init_field(self, j):
        if j not in self.ctx.app_data.fields:
            mode = 'ignore'
            terms = [[t,t] for t in self.ctx.__dataManager.get_terms(j)]
            self.ctx.app_data.fields[j] = {'mode': mode, 'terms': terms}
        else:
            for t in self.ctx.__dataManager.get_terms(j):
                if not any(a[0] == t for a in self.ctx.app_data.fields[j]['terms']):
                    self.ctx.app_data.fields[j]['terms'].append([t,t])
            for k, term_usage in enumerate(self.ctx.app_data.fields[j]['terms']):
                if term_usage[0] not in self.ctx.__dataManager.get_terms(j):
                    self.ctx.app_data.fields[j]['terms'].pop(k)

    def update_fields_list(self):
        self._field_list_being_updated = True
        
        self.fields_list.clear()
        for j, cat in enumerate(self.ctx.app_data.peopledata_keys):
            new_item = QListWidgetItem()
            new_item.setData(Qt.UserRole, j)
            new_item.setText(cat)
            self.fields_list.addItem(new_item)

        self._field_list_being_updated = False

    def update_mode_box(self, j):
        index = self.mode_box.findData(self.ctx.app_data.fields[j]['mode'])
        self.mode_box.setCurrentIndex(index)

    def update_terms_group(self, j):
        self._table_being_updated = True
        self.terms_table.setRowCount(len(self.ctx.app_data.fields[j]['terms']))
        for k, term_usage in enumerate(self.ctx.app_data.fields[j]['terms']):
            item_col0 = QTableWidgetItem(term_usage[0])
            item_col0.setFlags(Qt.ItemIsSelectable)
            self.terms_table.setItem(k, 0, item_col0)
            self.terms_table.setItem(k, 1, QTableWidgetItem(term_usage[1]))
        self._table_being_updated = False

    def status_mode_box(self, status):
        self.mode_group.setDisabled(not status)

    def status_terms_group(self, status):
        self.terms_group.setDisabled(not status)
        self.terms_layout.setCurrentIndex(1 if status else 0)

    def userchanged_field_list(self, index1, index2):
        if self._field_list_being_updated: return
        j = self.get_current_field_index()
        self.init_field(j)

        self.update_mode_box(j)
        self.update_terms_group(j)

        self.status_mode_box(True)
        mode = self.ctx.app_data.fields[j]['mode']
        self.status_terms_group(True if mode in ['cluster', 'diversify'] else False)

    def userchanged_mode_box(self, index):
        j = self.get_current_field_index()
        mode = self.mode_box.currentData()

        self.ctx.app_data.fields[j]['mode'] = mode

        mode = self.ctx.app_data.fields[j]['mode']
        self.status_terms_group(True if mode in ['cluster', 'diversify'] else False)

        self.ctx.__mainWindow.__tabs.fields_update()

    def userchanged_table(self, k, l):
        if self._table_being_updated: return
        j = self.get_current_field_index()
        self.ctx.app_data.fields[j]['terms'][k][1] = self.terms_table.item(k, l).text()
