from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QFrame

from org.sortition.groupselect.gui.maintabs.fields.TAFieldsTab import TAFieldsTab
from org.sortition.groupselect.gui.maintabs.generate.TAGenerateTab import TAGenerateTab
from org.sortition.groupselect.gui.maintabs.peopledata.TAPeopleDataTab import TAPeopleDataTab
from org.sortition.groupselect.gui.maintabs.results.TAOutputTab import TAOutputTab


class TAMainTabs(QWidget):
    editted = False

    def __init__(self, ctx):
        super(QWidget, self).__init__()
        self.ctx = ctx

        self.__createUi()

    def __createUi(self):
        self.__tabPeopleData = TAPeopleDataTab(self.ctx)
        self.__tabFields = TAFieldsTab(self.ctx)

        self.__tabPeopleDataTab = QTabWidget()
        self.__tabPeopleDataTab.setTabPosition(QTabWidget.South)
        self.__tabPeopleDataTab.addTab(self.__tabPeopleData, "Data")
        self.__tabPeopleDataTab.addTab(self.__tabFields, "Fields")

        self.__tabGenerate = TAGenerateTab(self.ctx)
        self.__tabResults = TAOutputTab(self.ctx)

        self.__tabs = QTabWidget()
        self.__tabs.addTab(self.__tabPeopleDataTab, "People Data")
        self.__tabs.addTab(self.__tabGenerate, "Generate")
        self.__tabs.addTab(self.__tabResults, "Results")

        m = 10
        self.__layout = QVBoxLayout(self)
        self.__layout.setContentsMargins(m, m, m, m)
        self.__layout.addWidget(self.__tabs)
        self.setLayout(self.__layout)

    def fileOpened(self):
        self.__tabs.setCurrentIndex(0)

    def fileClosed(self):
        pass