from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout

from org.sortition.groupselect.gui.maintabs.peopledata.TAPeopleDataTab import TAPeopleDataTab
from org.sortition.groupselect.gui.maintabs.fields.TAFieldsTab import TAFieldsTab
from org.sortition.groupselect.gui.maintabs.generate.TAGenerateTab import TAGenerateTab
from org.sortition.groupselect.gui.maintabs.results.TAOutputTab import TAOutputTab

class TAMainTabs(QWidget):
    editted = False

    def __init__(self, ctx):
        super(QWidget, self).__init__()
        self.ctx = ctx

        self.__tab_peopledata = TAPeopleDataTab(ctx)
        self.__tab_fields = TAFieldsTab(ctx)
        self.__tab_generate = TAGenerateTab(ctx)
        self.__tab_results = TAOutputTab(ctx)

        self.__tabs = QTabWidget()
        self.__tabs.addTab(self.__tab_peopledata, "People Data")
        self.__tabs.addTab(self.__tab_fields, "Fields")
        self.__tabs.addTab(self.__tab_generate, "Generate")
        self.__tabs.addTab(self.__tab_results, "Results")

        self.__layout = QVBoxLayout(self)
        self.__layout.addWidget(self.__tabs)
        self.setLayout(self.__layout)

    def file_opened(self):
        self.__tabs.setCurrentIndex(0)

    def file_closed(self):
        pass

    def peopledata_updated(self):
        self.__tab_fields.update_fields_list()
        self.__tab_fields.display_none()
        self.__tab_generate.update_field_order_lists()
        self.__tab_generate.update_manuals_list()

    def fields_update(self):
        self.__tab_generate.update_field_order_lists()

    def results_updated(self):
        self.__tab_results.display_data()
        self.__tab_results.update_tables_from_data()
