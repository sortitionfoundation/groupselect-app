from PyQt5.QtWidgets import QMenuBar, QAction

from org.sortition.groupselect.gui.mainmenu.TAHelpDialog import TAHelpDialog
from org.sortition.groupselect.gui.mainmenu.TAMainWindowDataActionHandler import TAMainWindowDataActionHandler
from org.sortition.groupselect.gui.mainmenu.TAMainWindowFileActionHandler import TAMainWindowFileActionHandler
from org.sortition.groupselect.gui.mainmenu.TAMainWindowResultsActionHandler import TAMainWindowResultsActionHandler


class TAMainMenu(QMenuBar):
    def __init__(self, ctx:'AppContext', main_window:'TAMainWindow', parent=None):
        super(TAMainMenu, self).__init__(parent)

        self.ctx = ctx
        self.mainWindow = main_window
        
        self.__file_action_handler = TAMainWindowFileActionHandler(self.ctx, self.mainWindow)
        self.__data_action_handler = TAMainWindowDataActionHandler(self.ctx, self.mainWindow)
        self.__results_action_handler = TAMainWindowResultsActionHandler(self.ctx, self.mainWindow)
        
        self.__setup_ui()
    
    def __setup_ui(self):
        # file menu
        file_menu = self.addMenu('File')

        # new
        action_item = QAction('New File', self)
        action_item.setShortcut("Ctrl+N")
        action_item.setStatusTip('Create a new GroupSelect file.')
        action_item.triggered.connect(self.__file_action_handler.newActionCall)
        file_menu.addAction(action_item)

        # open
        action_item = QAction('Open File...', self)
        action_item.setShortcut("Ctrl+O")
        action_item.setStatusTip('Open an existing GroupSelect file.')
        action_item.triggered.connect(self.__file_action_handler.openActionCall)
        file_menu.addAction(action_item)

        file_menu.addSeparator();

        # save
        action_item = QAction('Save', self)
        action_item.setShortcut("Ctrl+S")
        action_item.setStatusTip('Save changes to GroupSelect file.')
        action_item.triggered.connect(self.__file_action_handler.saveActionCall)
        file_menu.addAction(action_item)

        # save
        action_item = QAction('Save As...', self)
        action_item.setShortcut("Ctrl+Shift+S")
        action_item.setStatusTip('Save changes to GroupSelect file and specify target file.')
        action_item.triggered.connect(self.__file_action_handler.saveAsActionCall)
        file_menu.addAction(action_item)

        file_menu.addSeparator();

        # close
        action_item = QAction('Close File', self)
        action_item.setShortcut("Ctrl+W")
        action_item.setStatusTip('Close opened GroupSelect file.')
        action_item.triggered.connect(self.__file_action_handler.closeActionCall)
        file_menu.addAction(action_item)

        # quit
        action_item = QAction('Quit', self)
        action_item.setShortcut("Ctrl+Q")
        action_item.setStatusTip('Terminate the application')
        action_item.triggered.connect(self.__file_action_handler.quitActionCall)
        file_menu.addAction(action_item)

        # raw data menu
        self.__data_menu = self.addMenu('People Data')

        # Import
        action_item = QAction('Import from CSV...', self)
        action_item.setShortcut("Ctrl+I")
        action_item.setStatusTip('Import raw data to process.')
        action_item.triggered.connect(self.__data_action_handler.import_raw)
        self.__data_menu.addAction(action_item)

        # Export
        action_item = QAction('Export to CSV...', self)
        action_item.setShortcut("Ctrl+X")
        action_item.setStatusTip('Export your edited raw data to a file.')
        action_item.triggered.connect(self.__data_action_handler.export_raw)
        self.__data_menu.addAction(action_item)

        self.__data_menu.addSeparator();

        # Insert rows
        action_item = QAction('Insert rows...', self)
        action_item.setStatusTip('Insert new rows into the people\'s data table.')
        action_item.triggered.connect(self.__data_action_handler.insert_rows)
        self.__data_menu.addAction(action_item)

        # Insert cols
        action_item = QAction('Insert columns...', self)
        action_item.setStatusTip('Insert new columns into the people\'s data table.')
        action_item.triggered.connect(self.__data_action_handler.insert_cols)
        self.__data_menu.addAction(action_item)

        self.__data_menu.addSeparator();

        # Insert rows
        action_item = QAction('Delete selected rows', self)
        action_item.setStatusTip('Delete rows currently selected in the people\'s data table.')
        action_item.triggered.connect(self.__data_action_handler.delete_rows)
        self.__data_menu.addAction(action_item)

        # Insert rows
        action_item = QAction('Delete selected columns', self)
        action_item.setStatusTip('Delete columns currently selected in the people\'s data table.')
        action_item.triggered.connect(self.__data_action_handler.delete_cols)
        self.__data_menu.addAction(action_item)

        # results menu
        self.__results_menu = self.addMenu('Results')

        # Import
        action_item = QAction('Export selected...', self)
        action_item.setShortcut("Ctrl+E")
        action_item.setStatusTip('Export a single allocation to a CSV file.')
        action_item.triggered.connect(self.__results_action_handler.export_results_select)
        self.__results_menu.addAction(action_item)

        # Export
        action_item = QAction('Export all...', self)
        action_item.setShortcut("Ctrl+Shift+E")
        action_item.setStatusTip('Import all allocations to CSV files.')
        action_item.triggered.connect(self.__results_action_handler.export_results_all)
        self.__results_menu.addAction(action_item)

        # help menu
        help_menu = self.addMenu('Help')

        action_item = QAction('About...', self)
        action_item.setStatusTip('Show information about this software.')
        action_item.triggered.connect(self.__show_about_dialog)
        help_menu.addAction(action_item)

    def close_action_call(self):
        self.__file_action_handler.quitActionCall()

    def file_opened(self):
        self.__data_menu.setEnabled(True)
        if self.ctx.hasResults():
            self.__results_menu.setEnabled(True)

    def file_closed(self):
        self.__data_menu.setEnabled(False)
        self.__results_menu.setEnabled(False)

    def __show_about_dialog(self):
        about_html = open(self.ctx.get_resource("about.html")).read()
        TAHelpDialog.show(about_html, self)