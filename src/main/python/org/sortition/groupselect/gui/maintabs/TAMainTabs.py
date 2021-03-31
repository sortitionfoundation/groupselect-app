from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QGridLayout

from org.sortition.groupselect.gui.maintabs.generate.TAGenerateFieldsGroup import TAGenerateFieldsGroup
from org.sortition.groupselect.gui.maintabs.generate.TAGenerateSettingsGroup import TAGenerateSettingsGroup
from org.sortition.groupselect.gui.maintabs.peopledata.TAFieldsTab import TAFieldsTab
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

        self.__tabGenerateFieldsGroup = TAGenerateFieldsGroup(self.ctx)
        self.__tabGenerateSettingsGroup = TAGenerateSettingsGroup(self.ctx)
        generateLayout = QGridLayout()
        generateLayout.addWidget(self.__tabGenerateFieldsGroup, 0, 0)
        generateLayout.addWidget(self.__tabGenerateSettingsGroup, 1, 0)
        generateLayout.setRowStretch(0,1)
        generateWidget = QWidget()
        generateWidget.setLayout(generateLayout)

        self.__tabResults = TAOutputTab(self.ctx)

        self.__tabs = QTabWidget()
        self.__tabs.addTab(self.__tabPeopleDataTab, "People Data")
        self.__tabs.addTab(generateWidget, "Generate")
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