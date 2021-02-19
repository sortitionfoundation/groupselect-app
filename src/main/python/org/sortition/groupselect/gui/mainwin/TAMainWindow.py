import os.path

from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QStyleFactory

from org.sortition.groupselect.gui.mainwin.TAHelpDialog import TAHelpDialog
from org.sortition.groupselect.gui.mainwin.TAMainWindowFileActionHandler import TAMainWindowFileActionHandler
from org.sortition.groupselect.gui.mainwin.TAMainWindowDataActionHandler import TAMainWindowDataActionHandler
from org.sortition.groupselect.gui.mainwin.TAMainWindowResultsActionHandler import TAMainWindowResultsActionHandler
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

        self.createTaskBar()

        self.tabs = TAMainTabs(self.ctx)
        self.setCentralWidget(self.tabs)

    def createTaskBar(self):
        bar = self.menuBar()

        # file menu
        file_menu = bar.addMenu('File')
        self.file_action_handler = TAMainWindowFileActionHandler(self.ctx, self)

        # new
        action_item = QAction('New File', self)
        action_item.setShortcut("Ctrl+N")
        action_item.setStatusTip('Create a new GroupSelect file.')
        action_item.triggered.connect(self.file_action_handler.new_action_call)
        file_menu.addAction(action_item)

        # open
        action_item = QAction('Open File...', self)
        action_item.setShortcut("Ctrl+O")
        action_item.setStatusTip('Open an existing GroupSelect file.')
        action_item.triggered.connect(self.file_action_handler.open_action_call)
        file_menu.addAction(action_item)

        file_menu.addSeparator();

        # save
        action_item = QAction('Save', self)
        action_item.setShortcut("Ctrl+S")
        action_item.setStatusTip('Save changes to GroupSelect file.')
        action_item.triggered.connect(self.file_action_handler.save_action_call)
        file_menu.addAction(action_item)

        # save
        action_item = QAction('Save As...', self)
        action_item.setShortcut("Ctrl+Shift+S")
        action_item.setStatusTip('Save changes to GroupSelect file and specify target file.')
        action_item.triggered.connect(self.file_action_handler.save_as_action_call)
        file_menu.addAction(action_item)

        file_menu.addSeparator();

        # close
        action_item = QAction('Close File', self)
        action_item.setShortcut("Ctrl+W")
        action_item.setStatusTip('Close opened GroupSelect file.')
        action_item.triggered.connect(self.file_action_handler.close_action_call)
        file_menu.addAction(action_item)

        # quit
        action_item = QAction('Quit', self)
        action_item.setShortcut("Ctrl+Q")
        action_item.setStatusTip('Terminate the application')
        action_item.triggered.connect(self.file_action_handler.quit_action_call)
        file_menu.addAction(action_item)

        # raw data menu
        self.data_menu = bar.addMenu('People Data')
        self.data_action_handler = TAMainWindowDataActionHandler(self.ctx, self)

        # Import
        action_item = QAction('Import from CSV...', self)
        action_item.setShortcut("Ctrl+I")
        action_item.setStatusTip('Import raw data to process.')
        action_item.triggered.connect(self.data_action_handler.import_raw)
        self.data_menu.addAction(action_item)

        # Export
        action_item = QAction('Export to CSV...', self)
        action_item.setShortcut("Ctrl+X")
        action_item.setStatusTip('Export your edited raw data to a file.')
        action_item.triggered.connect(self.data_action_handler.export_raw)
        self.data_menu.addAction(action_item)

        self.data_menu.addSeparator();

        # Insert rows
        action_item = QAction('Insert rows...', self)
        action_item.setStatusTip('Insert new rows into the people\'s data table.')
        action_item.triggered.connect(self.data_action_handler.insert_rows)
        self.data_menu.addAction(action_item)

        # Insert cols
        action_item = QAction('Insert columns...', self)
        action_item.setStatusTip('Insert new columns into the people\'s data table.')
        action_item.triggered.connect(self.data_action_handler.insert_cols)
        self.data_menu.addAction(action_item)

        self.data_menu.addSeparator();

        # Insert rows
        action_item = QAction('Delete selected rows', self)
        action_item.setStatusTip('Delete rows currently selected in the people\'s data table.')
        action_item.triggered.connect(self.data_action_handler.delete_rows)
        self.data_menu.addAction(action_item)

        # Insert rows
        action_item = QAction('Delete selected columns', self)
        action_item.setStatusTip('Delete columns currently selected in the people\'s data table.')
        action_item.triggered.connect(self.data_action_handler.delete_cols)
        self.data_menu.addAction(action_item)

        # results menu
        self.results_menu = bar.addMenu('Results')
        self.results_action_handler = TAMainWindowResultsActionHandler(self.ctx, self)

        # Import
        action_item = QAction('Export selected...', self)
        action_item.setShortcut("Ctrl+E")
        action_item.setStatusTip('Export a single allocation to a CSV file.')
        action_item.triggered.connect(self.results_action_handler.export_results_select)
        self.results_menu.addAction(action_item)

        # Export
        action_item = QAction('Export all...', self)
        action_item.setShortcut("Ctrl+Shift+E")
        action_item.setStatusTip('Import all allocations to CSV files.')
        action_item.triggered.connect(self.results_action_handler.export_results_all)
        self.results_menu.addAction(action_item)

        # help menu
        help_menu = bar.addMenu('Help')

        action_item = QAction('About...', self)
        action_item.setStatusTip('Show information about this software.')
        action_item.triggered.connect(self.show_about_dialog)
        help_menu.addAction(action_item)

    def appStart(self):
        self.window_file_closed()
        self.show()

    def new_action_call(self):
        if self.confirm_discard(): self.ctx.new_file()

    def closeEvent(self, event):
        self.file_action_handler.close_action_call()

    def update_window_title(self):
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

    def window_file_opened(self):
        self.update_window_title()
        self.tabs.file_opened()
        self.data_menu.setEnabled(True)
        if self.ctx.hasResults():
            self.results_menu.setEnabled(True)

    def window_file_closed(self):
        self.update_window_title()
        self.tabs.file_closed()
        self.data_menu.setEnabled(False)
        self.results_menu.setEnabled(False)

    def window_file_saved(self):
        self.update_window_title()

    def show_about_dialog(self):
        about_html = open(self.ctx.get_resource("about.html")).read()
        TAHelpDialog.show(about_html, self)
