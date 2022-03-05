from PyQt5.QtWidgets import QMessageBox, QFileDialog, QErrorMessage

from org.sortition.groupselect.data.TAFileFormats import import_formats
from org.sortition.groupselect.data.TAFileImports import get_import_data
from org.sortition.groupselect.gui.mainmenu.TAInsertRowsColsDialog import TAInsertRowsColsDialog


class TAMainWindowDataActionHandler:
    def __init__(self, ctx: 'AppContext', main_window: 'TAMainWindow'):
        self.ctx = ctx
        self.mainWindow = main_window

    def confirm_discard_results(self):
        if self.ctx.app_data.results:
            reply = QMessageBox.question(self.mainWindow, 'Discard Results', 'Please be aware that this action will discard your current results. Proceed?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes: return True
            else: return False
        else: return True

    def importRaw(self):
        if not self.ctx.getStatus(): return
        if self.__confirmDiscardRaw():
            fname, scheme = QFileDialog.getOpenFileName(self.mainWindow, 'Import people data from file', None, import_formats)
            if not fname: return

            ok, keys, vals = get_import_data(fname, self.mainWindow)

            if not ok: return
            self.ctx.getPeopleDataModel().updateFromImport(keys, vals)
            self.ctx.changesToFile()

    def export_raw(self):
        if not self.ctx.getStatus(): return
        fname, scheme = QFileDialog.getSaveFileName(self.mainWindow, 'Export People Data to CSV', None, 'Comma-separated Values Files (*.csv)')
        if not fname: return
        if not fname.endswith('.csv'):
            fname += '.csv'
        try:
            with open(fname, 'w') as handle:
                self.ctx.__dataManager.export_raw_to_csv(handle)
                handle.close()
        except Exception as e:
            error_dialog = QErrorMessage()
            error_dialog.showMessage(str(e))

    def insert_rows(self):
        if not self.ctx.getStatus(): return
        if not self.confirm_discard_results(): return
        options = [(i, i+1) for i in range(self.ctx.app_data.m_data)]
        options.append((self.ctx.app_data.m_data, 'end'))
        ok, beforeRow, number = TAInsertRowsColsDialog.get_input(self.mainWindow, 'rows', options)
        if not ok: return
        self.ctx.__dataManager.insert_rows(beforeRow, number)
        self.ctx.changesToFile()
        self.mainWindow.__tabs.tab_peopledata.update_table_from_data()
        self.mainWindow.__tabs.peopledata_updated()
        self.mainWindow.__tabs.tab_results.display_empty()
        self.mainWindow.__tabs.results_updated()
        self.mainWindow.__resultsMenu.setEnabled(False)

    def insert_cols(self):
        if not self.ctx.getStatus(): return
        options = [(j, self.ctx.app_data.peopledata_keys[j]) for j in range(self.ctx.app_data.n_data)]
        options.append((self.ctx.app_data.n_data, 'end'))
        ok, beforeCol, number = TAInsertRowsColsDialog.get_input(self.mainWindow, 'cols', options)
        if not ok: return
        self.ctx.__dataManager.insert_cols(beforeCol, number)
        self.ctx.changesToFile()
        self.mainWindow.__tabs.tab_peopledata.update_table_from_data()
        self.mainWindow.__tabs.peopledata_updated()
        self.mainWindow.__tabs.tab_results.display_empty()
        self.mainWindow.__tabs.results_updated()
        self.mainWindow.__resultsMenu.setEnabled(False)

    def delete_rows(self):
        if not self.ctx.getStatus(): return
        if not self.confirm_discard_results(): return
        selection = self.mainWindow.__tabs.tab_peopledata.table_widget.selectionModel()
        rows = [index.row() for index in selection.selectedRows()]
        if not rows: return
        self.ctx.__dataManager.delete_rows(rows)
        self.ctx.changesToFile()
        self.mainWindow.__tabs.tab_peopledata.update_table_from_data()
        self.mainWindow.__tabs.peopledata_updated()
        self.mainWindow.__tabs.tab_results.display_empty()
        self.mainWindow.__tabs.results_updated()
        self.mainWindow.__resultsMenu.setEnabled(False)

    def delete_cols(self):
        if not self.ctx.getStatus(): return
        selection = self.mainWindow.__tabs.tab_peopledata.table_widget.selectionModel()
        cols = [index.column() for index in selection.selectedColumns()]
        if not cols: return
        must_discard_results = self.ctx.__dataManager.cols_not_ignored(cols)
        if must_discard_results:
            if not self.confirm_discard_results(): return
        self.ctx.__dataManager.delete_cols(cols, must_discard_results)
        self.ctx.changesToFile()
        self.mainWindow.__tabs.tab_peopledata.update_table_from_data()
        self.mainWindow.__tabs.peopledata_updated()
        if must_discard_results: self.mainWindow.__tabs.tab_results.display_empty()
        self.mainWindow.__tabs.results_updated()
        self.mainWindow.__resultsMenu.setEnabled(False)

    def __confirmDiscardRaw(self):
        if self.ctx.hasPeople():
            reply = QMessageBox.question(self.mainWindow, 'Overwrite Content',
                                         'The data import will potentially overwrite existing raw data. Proceed?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes: return True
            else: return False
        else: return True