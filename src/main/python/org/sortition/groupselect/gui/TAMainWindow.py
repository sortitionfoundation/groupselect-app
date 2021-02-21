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
        label = QLabel("Please create a new file or open an existing one.")
        label.setAlignment(Qt.AlignCenter)

        stackedWidget = QWidget()
        self.stackedLayout = QStackedLayout()
        self.stackedLayout.addWidget(label)
        self.stackedLayout.addWidget(self.__tabs)
        stackedWidget.setLayout(self.stackedLayout)
        self.setCentralWidget(stackedWidget)

    def appStart(self):
        self.windowFileClosed()
        self.show()

    def closeEvent(self, event):
        self.__mainMenu.close_action_call()

    def windowFileOpened(self):
        self.__updateWindowTitle()

        self.__tabs.fileOpened()
        self.__mainMenu.fileOpened()

        self.stackedLayout.setCurrentIndex(1)

    def windowFileClosed(self):
        self.__updateWindowTitle()

        self.__tabs.fileClosed()
        self.__mainMenu.file_closed()

        self.stackedLayout.setCurrentIndex(0)

    def window_file_saved_or_unsaved(self):
        self.__updateWindowTitle()

    def __updateWindowTitle(self):
        if self.ctx.getStatus():
            if self.ctx.issetFname():
                fnameWinTitle = os.path.basename(self.ctx.getFname())
                if self.ctx.isUnsaved():
                    fnameWinTitle += '*'
            else:
                fnameWinTitle = "Unsaved File"
                if self.ctx.isUnsaved():
                    fnameWinTitle += '*'
            newTitle = '{} — GroupSelect'.format(fnameWinTitle)
        else:
            newTitle = 'GroupSelect'
        self.setWindowTitle(newTitle)
