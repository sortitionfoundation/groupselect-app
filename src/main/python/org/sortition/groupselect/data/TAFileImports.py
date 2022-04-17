from PyQt5.QtWidgets import QErrorMessage

from org.sortition.groupselect.data.TAFileFormats import formats_mapping


def get_import_data(main_window: 'TAMainWindow', fname: str):
    for forname, fordict in formats_mapping.items():
        if fordict['importable'] and any(fname.endswith(f".{ending}") for ending in fordict['endings']):
            return *fordict['handler'].get_input(main_window, fname), forname

    QErrorMessage(main_window).showMessage(str('Unknown file type.'))
    return False, None, None, None, None


def get_import_data_quick(main_window: 'TAMainWindow', fname: str, forname: str, options: dict):
    handler = formats_mapping[forname]['handler']
    return *handler.get_quick(main_window, fname, options), forname