from org.sortition.groupselect.gui.mainmenu.import_dialogs.TACSVImportDialog import TACSVImportDialog
from org.sortition.groupselect.gui.mainmenu.import_dialogs.TASpreadsheetImportDialog import TASpreadsheetImportDialog


formats_mapping = {
    'native': {
        'name': 'GroupSelect 2 Files',
        'endings': ['gsf2'],
        'importable': False,
        'saveable': True,
    },
    'delim-separated': {
        'name': 'Comma-separated values files',
        'endings': ['csv', 'tsv', 'psv', 'ssv', 'dsv'],
        'importable': True,
        'saveable': False,
        'handler': TACSVImportDialog,
    },
    'open-document': {
        'name': 'Open-document spreadsheet',
        'endings': ['ods'],
        'importable': True,
        'saveable': False,
        'handler': None,
    },
    'ms-office': {
        'name': 'MS Excel spreadsheet',
        'endings': ['xls', 'xlsx'],
        'importable': True,
        'saveable': False,
        'handler': TASpreadsheetImportDialog,
    },
}


def __getFormats(formats: list):
    return ';;'.join(
        ['All allowed file formats (' + ' '.join(f"*.{e}" for forname, fordict in formats_mapping.items() if forname in formats for e in fordict['endings']) + ')'] +
        [fordict['name'] + '(' + ' '.join(f"*.{e}" for e in fordict['endings']) + ')' for forname, fordict in formats_mapping.items() if forname in formats]
    )


file_formats = __getFormats(list(formats_mapping.keys()))
import_formats = __getFormats([forname for forname, fordict in formats_mapping.items() if fordict['importable']])
save_formats = __getFormats([forname for forname, fordict in formats_mapping.items() if fordict['saveable']])


def determineFormatFromFname(fname: str):
    for forname, fordict in formats_mapping.items():
        if any(fname.endswith('.' + e) for e in fordict['endings']):
            return forname
