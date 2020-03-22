from PyQt5.QtCore import QDateTime, Qt, QTimer, QObject
from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QStyleFactory, QWidget, QPushButton, QTabWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QLabel, QMessageBox, QFileDialog, QInputDialog, QLineEdit, QTableWidgetItem, QErrorMessage, QListWidget, QComboBox, QGroupBox, QGridLayout, QFormLayout, QScrollArea, QAbstractItemView)
from PyQt5.QtGui import QIntValidator, QDoubleValidator

import pickle
import traceback

from org.sortition.tableallocations.gui.maintabs.peopledata.TAPeopleDataTab import TAPeopleDataTab
from org.sortition.tableallocations.gui.maintabs.fields.TAFieldsTab import TAFieldsTab
from org.sortition.tableallocations.gui.maintabs.generate.TAGenerateTab import TAGenerateTab
from org.sortition.tableallocations.gui.maintabs.results.TAOutputTab import TAOutputTab

class TAMainTabs(QWidget):
    editted = False

    def __init__(self, ctx):
        super(QWidget, self).__init__()
        self.ctx = ctx
        self.layout = QVBoxLayout(self)

        self.tab_peopledata = TAPeopleDataTab(ctx)
        self.tab_fields = TAFieldsTab(ctx)
        self.tab_generate = TAGenerateTab(ctx)
        self.tab_results = TAOutputTab(ctx)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.tab_peopledata, "People Data")
        self.tabs.addTab(self.tab_fields, "Fields")
        self.tabs.addTab(self.tab_generate, "Generate")
        self.tabs.addTab(self.tab_results, "Results")

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        self.initialiseOnStart()

    def initialiseOnStart(self):
        self.setDisabled(True)
        self.tab_results.display_empty()

    def file_opened(self):
        self.setDisabled(False)
        self.tab_peopledata.update_table_from_data()
        self.peopledata_updated()
        self.tab_peopledata.display_table()
        self.tab_generate.update_settings()
        self.tab_results.update_tables_from_data()
        self.tab_results.display_data()
        self.tabs.setCurrentIndex(0)

    def file_closed(self):
        self.setDisabled(True)
        self.tab_peopledata.update_table_from_data()
        self.peopledata_updated()
        self.tab_peopledata.display_empty()
        self.tabs.setCurrentIndex(0)

    def peopledata_updated(self):
        self.tab_fields.update_fields_list()
        self.tab_fields.display_none()
        self.tab_generate.update_field_order_lists()
        self.tab_generate.update_manuals_list()

    def fields_update(self):
        self.tab_generate.update_field_order_lists()

    def results_updated(self):
        self.tab_results.display_data()
        self.tab_results.update_tables_from_data()
