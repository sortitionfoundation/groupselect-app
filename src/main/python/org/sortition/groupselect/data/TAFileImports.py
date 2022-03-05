from PyQt5.QtWidgets import QErrorMessage

from org.sortition.groupselect.gui.mainmenu.import_dialogs.TACSVImportDialog import TACSVImportDialog
from org.sortition.groupselect.gui.mainmenu.import_dialogs.TASpreadsheetImportDialog import TASpreadsheetImportDialog


def get_import_data(fname: str, main_window: 'TAMainWindow'):
    if any(fname.endswith(f".{ending}") for ending in ['csv', 'tsv']):
        return TACSVImportDialog.get_input(main_window, fname)
    elif any(fname.endswith(f".{ending}") for ending in ['xls', 'xlsx']):
        return TASpreadsheetImportDialog.get_input(main_window, fname)
    else:
        QErrorMessage(main_window).showMessage(str('Unknown file type.'))
        return False, None, None