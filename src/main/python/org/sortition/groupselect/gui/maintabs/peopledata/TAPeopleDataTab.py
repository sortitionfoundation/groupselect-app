from PyQt5.QtCore import Qt
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTableWidget, QLabel, QInputDialog, QLineEdit, QTableWidgetItem, \
    QStackedLayout, QTableView


class TAPeopleDataTab(QWidget):
    def __init__(self, ctx):
        super(TAPeopleDataTab, self).__init__()
        self.ctx = ctx

        self.table_being_updated = False

        stacked_widget = QWidget()
        self.stacked_layout = QStackedLayout()
        self.stacked_layout.addWidget(self.create_empty_widget())
        self.stacked_layout.addWidget(self.create_data_widget())
        stacked_widget.setLayout(self.stacked_layout)

        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(stacked_widget)
        self.setLayout(layout)

    def display_empty(self):
        self.stacked_layout.setCurrentIndex(0)

    def display_table(self):
        self.stacked_layout.setCurrentIndex(1)

    def create_empty_widget(self):
        label = QLabel("Please create a new file or open existing one.")
        label.setAlignment(Qt.AlignCenter)

        return label

    def create_data_widget(self):
        self.table_widget = QTableView()
        self.table_widget.setModel(self.ctx.getPeopleDataModel())
        self.table_widget.horizontalHeader().sectionDoubleClicked.connect(self.update_cat_key)

        # TODO: add cell changed trigger
        #self.table_widget.model().cellChanged.connect(self.ctx.set_unsaved)

        return self.table_widget

    def update_cat_key(self, j):
        old_key = self.table_widget.model().getCatKey(j)
        new_key, ok = QInputDialog.getText(self, 'Change label for column %d' % j, 'New label for column:', QLineEdit.Normal, old_key)
        if not ok: return

        #self.table_widget.horizontalHeaderItem(j).setText(new_key)
        #self.ctx.app_data.peopledata_keys[j] = new_key
        self.table_widget.model().updateFieldName(j, new_key)
        self.table_widget.model().headerDataChanged.emit(QtCore.Qt.Horizontal, 0, 2)
        self.ctx.set_unsaved()
        #self.ctx.window.tabs.peopledata_updated()

        print(self.table_widget.model())
        print(self.ctx.app_data.peopleDataModel)

    def update_table_from_data(self):
        self.table_widget.setModel(self.ctx.app_data.peopleDataModel)
        return

        if not self.ctx.app_data:
            self.table_widget.setRowCount(0)
            self.table_widget.setColumnCount(0)
            return

        m_data = self.ctx.app_data.m_data
        n_data = self.ctx.app_data.n_data

        self.table_widget.setRowCount(m_data)
        self.table_widget.setColumnCount(n_data)

        self.table_being_updated = True
        self.table_widget.clear()
        self.table_widget.setRowCount(m_data);
        self.table_widget.setColumnCount(n_data);
        for i in range(m_data):
            for j in range(n_data):
                self.table_widget.setItem(i, j, QTableWidgetItem(self.ctx.app_data.peopledata_vals[i][j]))
        self.table_being_updated = False

        self.table_widget.setHorizontalHeaderLabels([cat for cat in self.ctx.app_data.peopledata_keys])
