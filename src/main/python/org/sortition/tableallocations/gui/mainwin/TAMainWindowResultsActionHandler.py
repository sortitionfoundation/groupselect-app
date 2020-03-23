import sys, os.path

from PyQt5.QtWidgets import QMessageBox, QFileDialog, QInputDialog, QErrorMessage

class TAMainWindowResultsActionHandler:
    def __init__(self, ctx, window):
        self.ctx = ctx
        self.win = window

    def export_results_select(self):
        if not self.ctx.app_data.results: return
        fname, scheme = QFileDialog.getSaveFileName(self.win, 'Export Allocation to CSV', None, "Comma-separated Values Files (*.csv)")
        if not fname: return
        if not fname.endswith('.csv'):
            fname += '.csv'
        try:
            with open(fname, 'w') as handle:
                a = self.ctx.window.tabs.tab_results.tabs.currentIndex()
                self.ctx.app_data_manager.export_allocation_to_csv(handle, a)
                handle.close()
        except Exception as e:
            error_dialog = QErrorMessage()
            error_dialog.showMessage(str(e))

    def export_results_all(self):
        if not self.ctx.app_data.results: return
        dname = str(QFileDialog.getExistingDirectory(self.win, "Select Directory"))
        if not dname: return
        fbasename_tmp = os.path.basename(self.ctx.filesave_manager.get_fname()).rstrip('.taf') if self.ctx.filesave_manager.isset_fname() else 'New File'
        fbasename_tmp += ' Results #.csv'
        fbasename, ok = QInputDialog.getText(self.win, 'Enter File Base Name', 'Please enter the CSV file base name for export below.', text=fbasename_tmp)
        if not ok: return
        if not fbasename.endswith('.csv'):
            fbasename += '.csv'

        files = []
        for a in range(len(self.ctx.app_data.results)):
            fname = fbasename.replace('#', str(a+1))
            files.append((a, fname))

        if any(os.path.isfile(fname) for a, fname in files):
            reply = QMessageBox.question(self.win, 'Overwrite File', "Some of the output files already exist. Would you like to proceed?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        try:
            for a, fname in files:
                with open(fname, 'w') as handle:
                    self.ctx.app_data_manager.export_allocation_to_csv(handle, a)
                    handle.close()
        except Exception as e:
            error_dialog = QErrorMessage()
            error_dialog.showMessage(str(e))
