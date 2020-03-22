from PyQt5.QtCore import QDateTime, Qt, QTimer, QObject
from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QStyleFactory, QWidget, QPushButton, QTabWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QLabel, QMessageBox, QFileDialog, QInputDialog, QLineEdit, QTableWidgetItem, QErrorMessage, QListWidget, QComboBox, QGroupBox, QGridLayout, QFormLayout, QScrollArea, QAbstractItemView, QStackedLayout, QCheckBox, QListWidgetItem)
from PyQt5.QtGui import QIntValidator, QDoubleValidator

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
        self.table_widget = QTableWidget()
        self.table_widget.horizontalHeader().sectionDoubleClicked.connect(self.update_cat_key)
        self.table_widget.cellChanged.connect(self.update_data_from_table)

        return self.table_widget

    def update_cat_key(self, n_tab):
        old_key = self.table_widget.horizontalHeaderItem(n_tab).text()
        new_key, ok = QInputDialog.getText(self, 'Change label for column %d' % n_tab, 'New label for column:',                                                        QLineEdit.Normal, old_key)
        if not ok: return

        self.table_widget.horizontalHeaderItem(n_tab).setText(new_key)
        self.ctx.app_data.peopledata_keys[n_tab] = new_key
        self.ctx.set_unsaved()
        self.ctx.window.tabs.peopledata_updated()

    def update_table_from_data(self):
        if not self.ctx.app_data:
            self.table_widget.setRowCount(0)
            self.table_widget.setColumnCount(0)
            return

        m_data = self.ctx.app_data.m_data
        n_data = self.ctx.app_data.n_data

        self.table_widget.setRowCount(m_data)
        self.table_widget.setColumnCount(n_data)

        self.table_being_updated = True
        for i in range(m_data):
            for j in range(n_data):
                self.table_widget.setItem(i, j, QTableWidgetItem(self.ctx.app_data.peopledata_vals[i][j]))
        self.table_being_updated = False

        self.table_widget.setHorizontalHeaderLabels([cat for cat in self.ctx.app_data.peopledata_keys])

    def update_data_from_table(self, i, j):
        if self.table_being_updated: return
        self.ctx.app_data.peopledata_vals[i][j] = self.table_widget.item(i, j).text()
        self.ctx.set_unsaved()
        self.ctx.window.tabs.peopledata_updated()
