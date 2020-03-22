import sys, os.path

from PyQt5.QtWidgets import QMessageBox, QFileDialog, QErrorMessage

class TAMainWindowDataActionHandler:
    def __init__(self, ctx, window):
        self.ctx = ctx
        self.win = window

    def confirm_discard(self):
        if not self.ctx.app_data_manager.peopledata_is_empty():
            reply = QMessageBox.question(self.win, 'Overwrite Content', "The data import will overwrite all the raw data. Proceed?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes: return True
            else: return False
        else: return True

    def import_raw(self):
        if not self.ctx.get_status(): return
        if self.confirm_discard():
            fname, scheme = QFileDialog.getOpenFileName(self.win, 'Import People Data to CSV', None, "Comma-separated Values Files (*.csv)")
            if not fname: return
            try:
                with open(fname, 'r') as handle:
                    self.ctx.app_data_manager.import_raw_from_csv(handle)
            except Exception as e:
                error_dialog = QErrorMessage()
                error_dialog.showMessage(str(e))
                return
            self.ctx.set_unsaved()
            self.win.tabs.tab_peopledata.update_table_from_data()
            self.win.tabs.peopledata_updated()

    def export_raw(self):
        if not self.ctx.get_status(): return
        fname, scheme = QFileDialog.getSaveFileName(self.win, 'Export People Data to CSV', None, "Comma-separated Values Files (*.csv)")
        if not fname: return
        if not fname.endswith('.csv'):
            fname += '.csv'
        try:
            with open(fname, 'w') as handle:
                self.ctx.app_data_manager.export_raw_to_csv(handle)
                handle.close()
        except Exception as e:
            error_dialog = QErrorMessage()
            error_dialog.showMessage(str(e))
