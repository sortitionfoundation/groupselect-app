import sys, os.path

from PyQt5.QtWidgets import QMessageBox, QFileDialog

class TAMainWindowFileActionHandler:
    def __init__(self, ctx, window):
        self.ctx = ctx
        self.win = window

    def confirm_discard(self):
        if self.ctx.is_unsaved():
            reply = QMessageBox.question(self.win, 'Unsaved Changes', "Would you like to discard your unsaved changes?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes: return True
            else: return False
        else: return True

    def new_action_call(self):
        if self.confirm_discard():
            self.ctx.filesave_manager.new()
            self.ctx.set_status(True)
            self.win.window_file_opened()

    def open_action_call(self):
        if self.confirm_discard():
            fname, scheme = QFileDialog.getOpenFileName(self.win, 'Open Table-Allocations File', None, "Table-Allocations Files (*.taf)")
            if not fname: return
            try: self.ctx.filesave_manager.load_fname(fname)
            except Exception as ex:
                QMessageBox.critical(self.win, "Error", "Error while loading file: {}".format(str(ex)))
                return
            self.ctx.set_status(True)
            self.ctx.set_saved()
            self.win.window_file_opened()

    def save_action(self, request_fname=True):
        if request_fname or not self.ctx.filesave_manager.isset_fname():
            fname, scheme = QFileDialog.getSaveFileName(self.win, 'Save Table-Allocations File', None, "Table-Allocations Files (*.taf)")
            if not fname: return
            if not fname.endswith('.taf'):
                fname += '.taf'
            self.ctx.filesave_manager.set_fname(fname)
        try:
            self.ctx.filesave_manager.save()
        except Exception as ex:
            QMessageBox.critical(self.win, "Error", "Error while saving file: {}".format(str(ex)))
            return
        self.ctx.set_saved()
        self.win.update_window_title()

    def save_as_action_call(self):
        self.save_action()

    def save_action_call(self):
        self.save_action(request_fname=False)

    def close_action_call(self):
        if self.confirm_discard():
            self.ctx.set_status(False)
            self.ctx.set_saved()
            self.ctx.filesave_manager.close()
            self.win.window_file_closed()

    def quit_action_call(self):
        if self.confirm_discard():
            sys.exit()
