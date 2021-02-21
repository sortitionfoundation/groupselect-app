import os.path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QStyleFactory, QWidget, QStackedLayout, QLabel

from org.sortition.groupselect.gui.mainmenu.TAMainMenu import TAMainMenu
from org.sortition.groupselect.gui.maintabs.TAMainTabs import TAMainTabs

class TAMainWindow(QMainWindow):
    def __init__(self, ctx:'AppContext', parent=None):
        super(TAMainWindow, self).__init__(parent)
        self.ctx = ctx

        QApplication.setStyle(QStyleFactory.create('Fusion'))
        self.originalPalette = QApplication.palette()

        height = ctx.app.primaryScreen().size().height()
        width = ctx.app.primaryScreen().size().width()
        self.setGeometry(.1*width, .1*height, .8*width, .8*height)

        self.__mainMenu = TAMainMenu(self.ctx, self)
        self.setMenuBar(self.__mainMenu)

        self.__tabs = TAMainTabs(self.ctx)
        label = QLabel("Please create a new file or open existing one.")
        label.setAlignment(Qt.AlignCenter)

        stacked_widget = QWidget()
        self.stacked_layout = QStackedLayout()
        self.stacked_layout.addWidget(label)
        self.stacked_layout.addWidget(self.__tabs)
        stacked_widget.setLayout(self.stacked_layout)
        self.setCentralWidget(stacked_widget)

    def appStart(self):
        self.window_file_closed()
        self.show()

    def closeEvent(self, event):
        self.__mainMenu.close_action_call()

    def window_file_opened(self):
        self.__update_window_title()

        self.__tabs.file_opened()
        self.__mainMenu.file_opened()

        self.stacked_layout.setCurrentIndex(1)

    def window_file_closed(self):
        self.__update_window_title()

        self.__tabs.file_closed()
        self.__mainMenu.file_closed()

        self.stacked_layout.setCurrentIndex(0)

    def window_file_saved_or_unsaved(self):
        self.__update_window_title()

    def __update_window_title(self):
        if self.ctx.getStatus():
            if self.ctx.issetFname():
                fnameWinTitle = os.path.basename(self.ctx.filesave_manager.getFname())
                if self.ctx.is_unsaved():
                    fnameWinTitle += '*'
            else:
                fnameWinTitle = "Unsaved File"
                if self.ctx.is_unsaved():
                    fnameWinTitle += '*'
            newTitle = '{} — GroupSelect'.format(fnameWinTitle)
        else:
            newTitle = 'GroupSelect'
        self.setWindowTitle(newTitle)
