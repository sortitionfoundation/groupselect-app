"""Table model for editing term mappings of one field's raw values."""

from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from base_app.AbstractProjectModel import AbstractProjectModel

from GSProject import GSProject


class GSParticipantsTermsModel(
    QtCore.QAbstractTableModel, AbstractProjectModel
):
    """Table mapping the raw values found in one field to display terms."""

    _project: GSProject

    def __init__(self):
        """Initialise the model with no field selected."""
        super(GSParticipantsTermsModel, self).__init__()
        self._current_key = None
        self._tmp_terms = None

    def updated_project(self, project: GSProject):
        """Bind the model to a (newly opened) project."""
        self._project = project
        self._current_key = None
        self._tmp_terms = None
        self.layoutChanged.emit()

    def updated_pdata(self):
        """Refresh the term list for the current field, if any, from data."""
        if self._current_key is not None:
            self._tmp_terms = self._get_terms_for_current_key()
        self.layoutChanged.emit()

    # externally invoked data updates
    def update_key(self, key: None | int):
        """Switch to editing the term mapping for a different field."""
        self._current_key = key
        self._tmp_terms = self._get_terms_for_current_key()
        if key not in self._project.terms:
            self._project.terms[key] = self._tmp_terms
        self.layoutChanged.emit()

    # abstract method implementations
    def data(self, index, role):
        """Return the term found or its mapped usage for display or editing."""
        if self._tmp_terms is None:
            return None

        if (
            role == Qt.ItemDataRole.DisplayRole
            or role == Qt.EditRole
            or role == Qt.ForegroundRole
        ):
            term_found, term_used = self._tmp_terms[index.row()]
            if not index.column():
                ret = term_found
            else:
                ret = term_used
            if not ret:
                if role == Qt.ForegroundRole:
                    return QColor(Qt.gray)
                ret = "(empty)"
            if role == Qt.ForegroundRole:
                return QColor(Qt.black)
            return ret

    def rowCount(self, index):
        """Return the number of distinct terms found in the current field."""
        if self._tmp_terms is None:
            return 0

        if self._current_key is None or not self._tmp_terms:
            return 0
        else:
            return len(self._tmp_terms)

    def columnCount(self, index):
        """Return 2: the term found, and the term it is mapped to."""
        return 2

    def headerData(self, col, orientation, role):
        """Return the column header naming the found or usage term."""
        if (
            orientation == QtCore.Qt.Orientation.Horizontal
            and role == QtCore.Qt.ItemDataRole.DisplayRole
        ):
            return "Terms found" if not col else "Term usage"

    def setData(self, index, value, role=QtCore.Qt.ItemDataRole.DisplayRole):
        """Update the display term mapped to a found term."""
        if role != QtCore.Qt.ItemDataRole.EditRole or index.column() != 1:
            return False

        tf, tu = self._tmp_terms[index.row()]
        self._tmp_terms[index.row()] = (tf, value)

        return False

    def flags(self, index):
        """Return flags marking only the usage-term column as editable."""
        if index.column() == 0:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        else:
            return (
                Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsEditable
            )

    def _get_terms_for_current_key(self):
        terms = (
            self._project.terms[self._current_key]
            if self._current_key in self._project.terms
            else []
        )

        self._update_terms_from_data(self._current_key, terms)

        return terms

    def _update_terms_from_data(self, j, current_terms):
        terms_fresh = sorted(self._project.pdata.iloc[:, j].unique().tolist())

        for t_new in terms_fresh:
            if t_new not in [
                term_found for term_found, term_used in current_terms
            ]:
                current_terms.append((t_new, t_new))

        for term_found, term_used in current_terms:
            if term_found not in terms_fresh:
                current_terms.remove((term_found, term_used))

        check_empty = [term_found for term_found, term_used in current_terms]
        if "" in check_empty:
            empty_entry = check_empty.index("")
            _, term_used_for_empty = current_terms[empty_entry]
            del current_terms[empty_entry]
            current_terms.append(("", term_used_for_empty))
