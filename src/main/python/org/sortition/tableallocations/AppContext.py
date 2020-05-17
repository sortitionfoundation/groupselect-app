from fbs_runtime.application_context.PyQt5 import ApplicationContext, cached_property

from org.sortition.tableallocations.gui.mainwin.TAMainWindow import TAMainWindow
from org.sortition.tableallocations.data.TAAppDataManager import TAAppDataManager
from org.sortition.tableallocations.data.TAFileSaveManager import TAFileSaveManager
from org.sortition.tableallocations.allocator.TAAllocationsManager import TAAllocationsManager

class AppContext(ApplicationContext):
    def __init__(self, *args, **kwargs):
        super(AppContext, self).__init__(*args, **kwargs)

        self._status = False
        self._changed = False

        self.app_data = None

        self.app_data_manager = TAAppDataManager(self)
        self.ta_manager = TAAllocationsManager(self)
        self.filesave_manager = TAFileSaveManager(self)

        self.filesave_manager.close()

        self.window = TAMainWindow(self)

    def run(self):
        self.window.show()
        return self.app.exec_()

    @cached_property
    def main_window(self):
        return MainWindow(self)

    ### app state methods
    def get_status(self):
        return self._status

    def set_status(self, status):
        self._status = status

    def is_unsaved(self):
        return self._changed

    def set_unsaved(self):
        self._changed = True
        self.window.update_window_title()

    def set_saved(self):
        self._changed = False