from PyQt5.QtCore import QDateTime, Qt, QTimer, QObject
from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QStyleFactory, QWidget, QPushButton, QTabWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QLabel, QMessageBox, QFileDialog, QInputDialog, QLineEdit, QTableWidgetItem, QErrorMessage, QListWidget, QComboBox, QGroupBox, QGridLayout, QFormLayout, QScrollArea, QAbstractItemView, QStackedLayout, QCheckBox, QListWidgetItem)
from PyQt5.QtGui import QIntValidator, QDoubleValidator

from org.sortition.groupselect.gui.maintabs.results.TAAllocationOutputTab import TAAllocationOutputTab

class TAOutputTab(QWidget):
    def __init__(self, ctx):
        super(TAOutputTab, self).__init__()
        self.ctx = ctx

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

    def display_data(self):
        self.stacked_layout.setCurrentIndex(1)

    def create_empty_widget(self):
        label = QLabel("You first have to successfully run the allocation.")
        label.setAlignment(Qt.AlignCenter)

        return label

    def create_data_widget(self):
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.South)
        return self.tabs

    def not_empty(self):
        m_tab = self.tableWidget.rowCount()
        n_tab = self.tableWidget.columnCount()
        return any(self.tableWidget.item(i, j).text() for j in range(n_tab) for i in range(m_tab))

    def update_tables_from_data(self):
        for i in range(self.tabs.count()):
            self.tabs.removeTab(0)

        for i in range(len(self.ctx.app_data.results)):
            self.tabs.addTab(TAAllocationOutputTab(self.ctx, i), "Allocation {}".format(i+1))

        return
