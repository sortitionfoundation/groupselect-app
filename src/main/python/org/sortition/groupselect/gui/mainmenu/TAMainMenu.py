from PyQt5.QtWidgets import QMenuBar, QAction

from org.sortition.groupselect.gui.mainmenu.TAHelpDialog import TAHelpDialog
from org.sortition.groupselect.gui.mainmenu.TAMainWindowDataActionHandler import TAMainWindowDataActionHandler
from org.sortition.groupselect.gui.mainmenu.TAMainWindowFileActionHandler import TAMainWindowFileActionHandler
from org.sortition.groupselect.gui.mainmenu.TAMainWindowResultsActionHandler import TAMainWindowResultsActionHandler


class TAMainMenu(QMenuBar):
    def __init__(self, ctx: 'AppContext', main_window: 'TAMainWindow', parent=None):
        super(TAMainMenu, self).__init__(parent)

        self.ctx = ctx
        self.mainWindow = main_window

        self.__fileActionHandler = TAMainWindowFileActionHandler(self.ctx, self.mainWindow)
        self.__dataActionHandler = TAMainWindowDataActionHandler(self.ctx, self.mainWindow)
        self.__resultsActionHandler = TAMainWindowResultsActionHandler(self.ctx, self.mainWindow)

        self.__setupUi()

    def __setupUi(self):
        # file menu
        fileMenu = self.addMenu('File')

        # new
        actionItem = QAction('New File', self)
        actionItem.setShortcut("Ctrl+N")
        actionItem.setStatusTip('Create a new GroupSelect file.')
        actionItem.triggered.connect(self.__fileActionHandler.newActionCall)
        fileMenu.addAction(actionItem)

        # open
        actionItem = QAction('Open File...', self)
        actionItem.setShortcut("Ctrl+O")
        actionItem.setStatusTip('Open an existing GroupSelect file.')
        actionItem.triggered.connect(self.__fileActionHandler.openActionCall)
        fileMenu.addAction(actionItem)

        fileMenu.addSeparator();

        # save
        actionItem = QAction('Save', self)
        actionItem.setShortcut("Ctrl+S")
        actionItem.setStatusTip('Save changes to GroupSelect file.')
        actionItem.triggered.connect(self.__fileActionHandler.saveActionCall)
        fileMenu.addAction(actionItem)

        # save
        actionItem = QAction('Save As...', self)
        actionItem.setShortcut("Ctrl+Shift+S")
        actionItem.setStatusTip('Save changes to GroupSelect file and specify target file.')
        actionItem.triggered.connect(self.__fileActionHandler.saveAsActionCall)
        fileMenu.addAction(actionItem)

        fileMenu.addSeparator();

        # close
        actionItem = QAction('Close File', self)
        actionItem.setShortcut("Ctrl+W")
        actionItem.setStatusTip('Close opened GroupSelect file.')
        actionItem.triggered.connect(self.__fileActionHandler.closeActionCall)
        fileMenu.addAction(actionItem)

        # quit
        actionItem = QAction('Quit', self)
        actionItem.setShortcut("Ctrl+Q")
        actionItem.setStatusTip('Terminate the application')
        actionItem.triggered.connect(self.__fileActionHandler.quitActionCall)
        fileMenu.addAction(actionItem)

        # raw data menu
        self.__dataMenu = self.addMenu('People Data')

        # Import
        actionItem = QAction('Import from file...', self)
        actionItem.setShortcut('Ctrl+I')
        actionItem.setStatusTip('Import raw data to process.')
        actionItem.triggered.connect(self.__dataActionHandler.importRaw)
        self.__dataMenu.addAction(actionItem)

        # Import
        actionItem = QAction('Quick import', self)
        actionItem.setShortcut('F5')
        actionItem.setStatusTip('Import raw data to process.')
        actionItem.triggered.connect(self.__dataActionHandler.importQuick)
        self.__dataMenu.addAction(actionItem)

        # Export
        actionItem = QAction('Export to file...', self)
        actionItem.setShortcut("Ctrl+X")
        actionItem.setStatusTip('Export your edited raw data to a file.')
        actionItem.triggered.connect(self.__dataActionHandler.export_raw)
        self.__dataMenu.addAction(actionItem)

        self.__dataMenu.addSeparator();

        # Insert rows
        actionItem = QAction('Insert rows...', self)
        actionItem.setStatusTip('Insert new rows into the people\'s data table.')
        actionItem.triggered.connect(self.__dataActionHandler.insert_rows)
        self.__dataMenu.addAction(actionItem)

        # Insert cols
        actionItem = QAction('Insert columns...', self)
        actionItem.setStatusTip('Insert new columns into the people\'s data table.')
        actionItem.triggered.connect(self.__dataActionHandler.insert_cols)
        self.__dataMenu.addAction(actionItem)

        self.__dataMenu.addSeparator();

        # Insert rows
        actionItem = QAction('Delete selected rows', self)
        actionItem.setStatusTip('Delete rows currently selected in the people\'s data table.')
        actionItem.triggered.connect(self.__dataActionHandler.delete_rows)
        self.__dataMenu.addAction(actionItem)

        # Insert rows
        actionItem = QAction('Delete selected columns', self)
        actionItem.setStatusTip('Delete columns currently selected in the people\'s data table.')
        actionItem.triggered.connect(self.__dataActionHandler.delete_cols)
        self.__dataMenu.addAction(actionItem)

        # results menu
        self.__resultsMenu = self.addMenu('Results')

        # Import
        actionItem = QAction('Export selected...', self)
        actionItem.setShortcut("Ctrl+E")
        actionItem.setStatusTip('Export a single allocation to a CSV file.')
        actionItem.triggered.connect(self.__resultsActionHandler.export_results_select)
        self.__resultsMenu.addAction(actionItem)

        # Export
        actionItem = QAction('Export all...', self)
        actionItem.setShortcut("Ctrl+Shift+E")
        actionItem.setStatusTip('Import all allocations to CSV files.')
        actionItem.triggered.connect(self.__resultsActionHandler.export_results_all)
        self.__resultsMenu.addAction(actionItem)

        # settings menu
        settingsMenu = self.addMenu('Settings')

        actionItem = QAction("Show term usage in table", self)
        actionItem.setCheckable(True)
        actionItem.setChecked(True)
        actionItem.triggered.connect(self.ctx.toggleFieldsView)
        settingsMenu.addAction(actionItem)

        # help menu
        helpMenu = self.addMenu('Help')

        actionItem = QAction('About...', self)
        actionItem.setStatusTip('Show information about this software.')
        actionItem.triggered.connect(self.__show_about_dialog)
        helpMenu.addAction(actionItem)

    def close_action_call(self):
        self.__fileActionHandler.quitActionCall()

    def fileOpened(self):
        self.__dataMenu.setEnabled(True)
        if self.ctx.hasResults():
            self.__resultsMenu.setEnabled(True)

    def file_closed(self):
        self.__dataMenu.setEnabled(False)
        self.__resultsMenu.setEnabled(False)

    def __show_about_dialog(self):
        aboutHtml = open(self.ctx.get_resource("about.html")).read()
        TAHelpDialog.show(aboutHtml, self)
