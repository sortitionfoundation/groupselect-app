from PyQt5.QtWidgets import QMessageBox, QFileDialog

from org.sortition.groupselect.data.TAFileFormats import file_formats, save_formats
from org.sortition.groupselect.data.TAFileImports import get_import_data
from org.sortition.groupselect.gui.mainmenu.TANewFileOptionsDialog import TANewFileOptionsDialog


class TAMainWindowFileActionHandler:
    def __init__(self, ctx: 'AppContext', main_window: 'TAMainWindow'):
        self.ctx = ctx
        self.mainWindow = main_window

    def newActionCall(self):
        if self.__confirmDiscard():
            ok, number, names = TANewFileOptionsDialog.get_input(self.mainWindow)
            if not ok: return
            self.ctx.newFileEmpty(number, names)

    def closeActionCall(self):
        if self.__confirmDiscard():
            self.ctx.closeFile()

    def quitActionCall(self):
        if self.__confirmDiscard():
            self.ctx.quit()

    def openActionCall(self):
        if self.__confirmDiscard():
            fname, scheme = QFileDialog.getOpenFileName(self.mainWindow, 'Open file', None, file_formats)
            if not fname: return

            if fname.endswith('.gsf2'):
                ex = self.ctx.loadFile(fname)
                if ex: QMessageBox.critical(self.mainWindow, 'Error', f"Error while loading file: {ex}")
            else:
                ok, keys, vals = get_import_data(fname, self.mainWindow)
                if ok: self.ctx.newFileImported(keys, vals)


    def saveAsActionCall(self):
        self.__saveAction(requested_fname=True)

    def saveActionCall(self):
        self.__saveAction(requested_fname=False)

    def __saveAction(self, requested_fname: bool = True):
        if requested_fname or not self.ctx.issetFname():
            fname, scheme = QFileDialog.getSaveFileName(self.mainWindow, 'Save GroupSelect File', None, save_formats)
            if not fname: return
            if not fname.endswith('.gsf2'):
                fname += '.gsf2'
        else:
            fname = None

        ex = self.ctx.saveFile(fname)
        if ex: QMessageBox.critical(self.mainWindow, 'Error', f"Error while saving file: {ex}")

    def __confirmDiscard(self):
        if self.ctx.isUnsaved():
            reply = QMessageBox.question(self.mainWindow, 'Unsaved Changes',
                                         'Would you like to discard your unsaved changes?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                return True
            else:
                return False
        else:
            return True
