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

    def set_status(self, status):
        self.__status = status

    def is_unsaved(self):
        return self.__changed

    def set_unsaved(self):
        self.__changed = True
        self.__mainWindow.window_file_saved_or_unsaved()

    def set_saved(self):
        self.__changed = False
        self.__mainWindow.window_file_saved_or_unsaved()

    def hasResults(self):
        return self.__dataManager.hasResults()

    def getFname(self):
        return self.__dataManager.getFname()

    def issetFname(self):
        return self.__dataManager.issetFname()

    ### getters for data models
    def getPeopleDataModel(self):
        return self.__dataManager.peopleDataModel

    def getFieldsListModel(self):
        return self.__dataManager.fieldsListModel

    def getTermsDataModel(self):
        return self.__dataManager.termsDataModel

    ### global actions
    def newFile(self):
        self.__dataManager.newFile()

        self.set_status(True)
        self.set_unsaved()
        self.__mainWindow.window_file_opened()

    def loadFile(self, fname):
        ex = self.__dataManager.loadFile(fname)

        if ex: return ex

        self.set_status(True)
        self.set_saved()
        self.__mainWindow.window_file_opened()

        return False

    def saveFile(self, fname):
        ex = self.__dataManager.saveFile(fname)

        if ex: return ex

        self.set_saved()
        self.__mainWindow.window_file_saved()

    def closeFile(self):
        self.__dataManager.closeFile()

        self.set_status(False)
        self.set_saved()
        self.__mainWindow.window_file_closed()

    def quit(self):
        sys.exit()