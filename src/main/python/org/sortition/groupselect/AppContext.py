from fbs_runtime.application_context.PyQt5 import ApplicationContext, cached_property

from org.sortition.groupselect.gui.mainwin.TAMainWindow import TAMainWindow
from org.sortition.groupselect.data.TAAppDataManager import TAAppDataManager
from org.sortition.groupselect.data.TAFileSaveManager import TAFileSaveManager
from org.sortition.groupselect.allocator.TAAllocationsManager import TAAllocationsManager

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
    def get_status(self):
        return self.__status

    def set_status(self, status):
        self.__status = status

    def is_unsaved(self):
        return self.__changed

    def set_unsaved(self):
        self.__changed = True
        self.__mainWindow.update_window_title()

    def set_saved(self):
        self.__changed = False
        self.__mainWindow.update_window_title()

    def hasResults(self):
        return self.__dataManager.hasResults()

    def fnameIsset(self):
        return self.__dataManager.filesave_manager.issetFname()

    ### getters for data models
    def getPeopleDataModel(self):
        return self.__dataManager.peopleDataModel

    def getFieldsListModel(self):
        return self.__dataManager.fieldsListModel

    def getTermsDataModel(self):
        return self.__dataManager.termsDataModel

    ### global actions
    def new_file(self):
        self.__dataManager.new()

        self.set_status(True)
        self.set_unsaved()
        self.__mainWindow.window_file_opened()

    def load_file(self, fname):
        ex = self.__dataManager.load_file(fname)

        if ex: return ex

        self.set_status(True)
        self.set_saved()
        self.__mainWindow.window_file_opened()

        return False

    def save_file(self, fname):
        ex = self.__dataManager.save_file(fname)

        if ex: return ex

        self.set_saved()
        self.__mainWindow.window_file_saved()
