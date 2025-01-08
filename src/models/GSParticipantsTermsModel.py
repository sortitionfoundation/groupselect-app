from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from AbstractProjectModel import AbstractProjectModel

from src.GSProject import GSProject


class GSParticipantsTermsModel(QtCore.QAbstractTableModel, AbstractProjectModel):
    _project: GSProject

    def __init__(self):
        super(GSParticipantsTermsModel, self).__init__()
        self._current_key = None
        self._tmp_terms = None

    def updated_project(self, project: GSProject):
        self._project = project
        self._current_key = None
        self._tmp_terms = None
        self.layoutChanged.emit()

    def updated_pdata(self):
        if self._current_key is not None:
            self._tmp_terms = self._get_terms_for_current_key()
        self.layoutChanged.emit()

    # externally invoked data updates
    def update_key(self, key: None | int):
        self._current_key = key
        self._tmp_terms = self._get_terms_for_current_key()
        if key not in self._project.terms:
            self._project.terms[key] = self._tmp_terms
        self.layoutChanged.emit()

    # abstract method implementations
    def data(self, index, role):
        if self._tmp_terms is None:
            return None

        if role == Qt.ItemDataRole.DisplayRole or role == Qt.EditRole or role == Qt.ForegroundRole:
            term_found, term_used = self._tmp_terms[index.row()]
            if not index.column():
                ret = term_found
            else:
                ret = term_used
            if not ret:
                if role == Qt.ForegroundRole: return QColor(Qt.gray)
                ret = '(empty)'
            if role == Qt.ForegroundRole: return QColor(Qt.black)
            return ret

    def rowCount(self, index):
        if self._tmp_terms is None:
            return 0

        if self._current_key is None or not self._tmp_terms:
            return 0
        else:
            return len(self._tmp_terms)

    def columnCount(self, index):
        return 2

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Orientation.Horizontal and role == QtCore.Qt.ItemDataRole.DisplayRole:
            return 'Terms found' if not col else 'Term usage'

    def setData(self, index, value, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if role != QtCore.Qt.ItemDataRole.EditRole or index.column() != 1:
            return False

        tf, tu = self._tmp_terms[index.row()]
        self._tmp_terms[index.row()] = (tf, value)

        return False

    def flags(self, index):
        if index.column() == 0:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        else:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable

    def _get_terms_for_current_key(self):
        terms = (
            self._project.terms[self._current_key]
            if self._current_key in self._project.terms else
            []
        )

        self._update_terms_from_data(self._current_key, terms)

        return terms

    def _update_terms_from_data(self, j, current_terms):
        terms_fresh = sorted(self._project.pdata.iloc[:, j].unique().tolist())

        for t_new in terms_fresh:
            if t_new not in [term_found for term_found, term_used in current_terms]:
                current_terms.append((t_new, t_new))

        for term_found, term_used in current_terms:
            if term_found not in terms_fresh:
                current_terms.remove((term_found, term_used))

        check_empty = [term_found for term_found, term_used in current_terms]
        if '' in check_empty:
            empty_entry = check_empty.index('')
            _, term_used_for_empty = current_terms[empty_entry]
            del current_terms[empty_entry]
            current_terms.append(('', term_used_for_empty))
