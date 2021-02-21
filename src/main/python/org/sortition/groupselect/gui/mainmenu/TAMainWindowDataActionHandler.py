from PyQt5.QtWidgets import QMessageBox, QFileDialog, QErrorMessage

from org.sortition.groupselect.gui.mainmenu.TAImportOptionsDialog import TAImportOptionsDialog
from org.sortition.groupselect.gui.mainmenu.TAInsertRowsColsDialog import TAInsertRowsColsDialog

class TAMainWindowDataActionHandler:
    def __init__(self, ctx, window):
        self.ctx = ctx
        self.win = window

    def confirm_discard(self):
        if not self.ctx.__dataManager.peopledata_is_empty():
            reply = QMessageBox.question(self.win, 'Overwrite Content', "The data import will overwrite all the raw data. Proceed?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes: return True
            else: return False
        else: return True

    def confirm_discard_results(self):
        if self.ctx.app_data.results:
            reply = QMessageBox.question(self.win, 'Discard Results', "Please be aware that this action will discard your current results. Proceed?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes: return True
            else: return False
        else: return True

    def import_raw(self):
        if not self.ctx.getStatus(): return
        if self.confirm_discard():
            fname, scheme = QFileDialog.getOpenFileName(self.win, 'Import People Data to CSV', None, "Comma-separated Values Files (*.csv)")
            if not fname: return
            ok, csv_format = TAImportOptionsDialog.get_input(self.win)
            if not ok: return
            try:
                with open(fname, 'r') as handle:
                    self.ctx.__dataManager.import_raw_from_csv(handle, csv_format)
            except Exception as e:
                error_dialog = QErrorMessage()
                error_dialog.showMessage(str(e))
                return
            self.ctx.set_unsaved()
            self.win.__tabs.tab_peopledata.update_table_from_data()
            self.win.__tabs.peopledata_updated()

    def export_raw(self):
        if not self.ctx.getStatus(): return
        fname, scheme = QFileDialog.getSaveFileName(self.win, 'Export People Data to CSV', None, "Comma-separated Values Files (*.csv)")
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
        ok, beforeRow, number = TAInsertRowsColsDialog.get_input(self.win, 'rows', options)
        if not ok: return
        self.ctx.__dataManager.insert_rows(beforeRow, number)
        self.ctx.set_unsaved()
        self.win.__tabs.tab_peopledata.update_table_from_data()
        self.win.__tabs.peopledata_updated()
        self.win.__tabs.tab_results.display_empty()
        self.win.__tabs.results_updated()
        self.win.__results_menu.setEnabled(False)

    def insert_cols(self):
        if not self.ctx.getStatus(): return
        options = [(j, self.ctx.app_data.peopledata_keys[j]) for j in range(self.ctx.app_data.n_data)]
        options.append((self.ctx.app_data.n_data, 'end'))
        ok, beforeCol, number = TAInsertRowsColsDialog.get_input(self.win, 'cols', options)
        if not ok: return
        self.ctx.__dataManager.insert_cols(beforeCol, number)
        self.ctx.set_unsaved()
        self.win.__tabs.tab_peopledata.update_table_from_data()
        self.win.__tabs.peopledata_updated()
        self.win.__tabs.tab_results.display_empty()
        self.win.__tabs.results_updated()
        self.win.__results_menu.setEnabled(False)

    def delete_rows(self):
        if not self.ctx.getStatus(): return
        if not self.confirm_discard_results(): return
        selection = self.win.__tabs.tab_peopledata.table_widget.selectionModel()
        rows = [index.row() for index in selection.selectedRows()]
        if not rows: return
        self.ctx.__dataManager.delete_rows(rows)
        self.ctx.set_unsaved()
        self.win.__tabs.tab_peopledata.update_table_from_data()
        self.win.__tabs.peopledata_updated()
        self.win.__tabs.tab_results.display_empty()
        self.win.__tabs.results_updated()
        self.win.__results_menu.setEnabled(False)

    def delete_cols(self):
        if not self.ctx.getStatus(): return
        selection = self.win.__tabs.tab_peopledata.table_widget.selectionModel()
        cols = [index.column() for index in selection.selectedColumns()]
        if not cols: return
        must_discard_results = self.ctx.__dataManager.cols_not_ignored(cols)
        if must_discard_results:
            if not self.confirm_discard_results(): return
        self.ctx.__dataManager.delete_cols(cols, must_discard_results)
        self.ctx.set_unsaved()
        self.win.__tabs.tab_peopledata.update_table_from_data()
        self.win.__tabs.peopledata_updated()
        if must_discard_results: self.win.__tabs.tab_results.display_empty()
        self.win.__tabs.results_updated()
        self.win.__results_menu.setEnabled(False)