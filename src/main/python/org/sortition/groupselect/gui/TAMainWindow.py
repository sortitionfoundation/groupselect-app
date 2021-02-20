import os.path

from PyQt5.QtWidgets import QApplication, QMainWindow, QStyleFactory

from org.sortition.groupselect.gui.mainmenu.TAMainMenu import TAMainMenu
from org.sortition.groupselect.gui.mainmenu.TAHelpDialog import TAHelpDialog
from org.sortition.groupselect.gui.maintabs.TAMainTabs import TAMainTabs

class TAMainWindow(QMainWindow):
    def __init__(self, ctx, parent=None):
        super(TAMainWindow, self).__init__(parent)
        self.ctx = ctx

        QApplication.setStyle(QStyleFactory.create('Fusion'))
        self.originalPalette = QApplication.palette()

        height = ctx.app.primaryScreen().size().height()
        width = ctx.app.primaryScreen().size().width()
        self.setGeometry(.1*width, .1*height, .8*width, .8*height)

        self.__mainMenu = TAMainMenu(self.ctx, self)
        self.setMenuBar(self.__mainMenu)

        self.tabs = TAMainTabs(self.ctx)
        self.setCentralWidget(self.tabs)

    def appStart(self):
        self.window_file_closed()
        self.show()

    def closeEvent(self, event):
        self.__mainMenu.close_action_call()

    def window_file_opened(self):
        self.__update_window_title()
        self.tabs.file_opened()
        self.__mainMenu.file_opened()

    def window_file_closed(self):
        self.__update_window_title()
        self.tabs.file_closed()
        self.__mainMenu.file_closed()

    def window_file_saved_or_unsaved(self):
        self.__update_window_title()

    def __update_window_title(self):
        if self.ctx.get_status():
            if self.ctx.fnameIsset():
                fname_win_title = os.path.basename(self.ctx.filesave_manager.getFname())
                if self.ctx.is_unsaved():
                    fname_win_title += '*'
            else:
                fname_win_title = "Unsaved File"
                if self.ctx.is_unsaved():
                    fname_win_title += '*'
            new_title = '{} — GroupSelect'.format(fname_win_title)
        else:
            new_title = 'GroupSelect'
        self.setWindowTitle(new_title)
