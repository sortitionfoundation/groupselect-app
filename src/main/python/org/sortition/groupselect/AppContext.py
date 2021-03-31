import sys

from fbs_runtime.application_context.PyQt5 import ApplicationContext

from org.sortition.groupselect.gui.TAMainWindow import TAMainWindow
from org.sortition.groupselect.data.TAAppDataManager import TAAppDataManager


class AppContext(ApplicationContext):
    def __init__(self, *args, **kwargs):
        super(AppContext, self).__init__(*args, **kwargs)

        self.__status = False
        self.__changed = False

        self.__dataManager = TAAppDataManager(self)
        self.__mainWindow = TAMainWindow(self)

    def run(self):
        self.__dataManager.appStart()
        self.__mainWindow.appStart()

        return self.app.exec_()

    ### app state methods
    def getStatus(self):
        return self.__status

    def setStatus(self, status):
        self.__status = status

    def isUnsaved(self):
        return self.__changed

    def setUnsaved(self):
        self.__changed = True

    def setSaved(self):
        self.__changed = False

    def hasResults(self):
        return self.__dataManager.hasResults()

    def getFname(self):
        return self.__dataManager.getFname()

    def issetFname(self):
        return self.__dataManager.issetFname()

    def toggleFieldsView(self, view_state: bool):
        self.__dataManager.setFieldsView(view_state)

    ### getters for data models
    def getPeopleDataModel(self):
        return self.__dataManager.peopleDataModel

    def getFieldsListModel(self):
        return self.__dataManager.fieldsListModel

    def getTermsDataModel(self):
        return self.__dataManager.termsDataModel

    def getFieldsModels(self):
        return self.__dataManager.getFieldsModels()

    def getManualsModel(self):
        return self.__dataManager.getManualsModel()

    ### global actions
    def newFile(self, number, names):
        self.__dataManager.newFile(number, names)

        self.setStatus(True)
        self.setUnsaved()
        self.__mainWindow.windowFileOpened()

    def loadFile(self, fname):
        ex = self.__dataManager.loadFile(fname)

        if ex: return ex

        self.setStatus(True)
        self.setSaved()
        self.__mainWindow.windowFileOpened()

        return False

    def saveFile(self, fname):
        ex = self.__dataManager.saveFile(fname)

        if ex: return ex

        self.setSaved()
        self.__mainWindow.windowFileSavedOrUnsaved()

    def changesToFile(self):
        self.setUnsaved()
        self.__mainWindow.windowFileSavedOrUnsaved()

    def closeFile(self):
        self.__dataManager.closeFile()

        self.setStatus(False)
        self.setSaved()
        self.__mainWindow.windowFileClosed()

    def quit(self):
        sys.exit()
