import sys

from PyQt5.QtWidgets import QMessageBox, QFileDialog

class TAMainWindowFileActionHandler:
    def __init__(self, ctx, main_window):
        self.ctx = ctx
        self.mainWindow = main_window

    def confirm_discard(self):
        if self.ctx.is_unsaved():
            reply = QMessageBox.question(self.mainWindow, 'Unsaved Changes', "Would you like to discard your unsaved changes?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes: return True
            else: return False
        else: return True

    def new_action_call(self):
        if self.confirm_discard():
            self.ctx.new_file()

    def open_action_call(self):
        if self.confirm_discard():
            fname, scheme = QFileDialog.getOpenFileName(self.mainWindow, 'Open GroupSelect File', None, "GroupSelect Files (*.gsf)")
            if not fname: return
            ex = self.ctx.load_file(fname)
            if ex: QMessageBox.critical(self.mainWindow, "Error", "Error while loading file: {}".format(str(ex)))

    def save_action(self, request_fname=True):
        if request_fname or not self.ctx.issetFname():
            fname, scheme = QFileDialog.getSaveFileName(self.mainWindow, 'Save GroupSelect File', None, "GroupSelect Files (*.gsf)")
            if not fname: return
            if not fname.endswith('.gsf'):
                fname += '.gsf'
        else: fname = None

        ex = self.ctx.save_file(fname)
        if ex: QMessageBox.critical(self.mainWindow, "Error", "Error while saving file: {}".format(str(ex)))

    def save_as_action_call(self):
        self.save_action(request_fname=True)

    def save_action_call(self):
        self.save_action(request_fname=False)

    def close_action_call(self):
        if self.confirm_discard():
            self.ctx.set_status(False)
            self.ctx.set_saved()
            self.ctx.filesave_manager.close()
            self.mainWindow.window_file_closed()

    def quit_action_call(self):
        if self.confirm_discard():
            sys.exit()
