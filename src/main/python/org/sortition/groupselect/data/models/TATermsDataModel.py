from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from org.sortition.groupselect.data.TAAppData import TAAppData


class TATermsDataModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None, *args):
        super(TATermsDataModel, self).__init__(parent, *args)
        self.__currentAppData = TAAppData()
        self.__currentKey = None
        self.__tmpTerms = None

    def updateAppData(self, current_app_data: TAAppData):
        self.__currentAppData = current_app_data
        self.__currentKey = None
        self.__tmpTerms = None

        self.layoutChanged.emit()

    def updateKey(self, key: int):
        self.__currentKey = key
        self.__tmpTerms = self.__getTermsForCurrentKey()
        self.layoutChanged.emit()

    def updatedPeopleData(self):
        if self.__currentKey is not None: self.__tmpTerms = self.__getTermsForCurrentKey()
        self.layoutChanged.emit()

    def data(self, index, role):
        if role == Qt.DisplayRole or role == Qt.EditRole or role == Qt.ForegroundRole:
            term_found, term_used = self.__tmpTerms[index.row()]
            if not index.column():
                r = term_found
            else:
                r = term_used
            if not r:
                if role == Qt.ForegroundRole: return QColor(Qt.gray)
                r = "(empty)"
            if role == Qt.ForegroundRole: return QColor(Qt.black)
            return QtCore.QVariant(r)

    def rowCount(self, index):
        if self.__currentKey is None or not self.__tmpTerms: return 0
        else: return len(self.__tmpTerms)

    def columnCount(self, index):
        return 2

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if col == 0:
                return QtCore.QVariant('Terms Found')
            else:
                return QtCore.QVariant('Terms Usage')

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.EditRole or index.column() != 1:
            return False

        if not self.__currentAppData.peopledata_terms[self.__currentKey]:
            self.__currentAppData.peopledata_terms[self.__currentKey] = self.__tmpTerms

        tf, tu = self.__tmpTerms[index.row()]
        self.__tmpTerms[index.row()] = (tf, value)

        return False

    def flags(self, index):
        if index.column() == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def __updateTermsFromData(self, j, current_terms):
        terms_fresh = sorted(list(set(self.__currentAppData.peopledata_vals[i][j] for i in range(len(self.__currentAppData.peopledata_vals)))))

        for t_new in terms_fresh:
            if t_new not in [term_found for term_found, term_used in current_terms]:
                current_terms.append((t_new, t_new))

        check_empty = [term_found for term_found, term_used in current_terms]
        if "" in check_empty:
            empty_entry = check_empty.index("")
            _, term_used_for_empty = current_terms[empty_entry]
            del current_terms[empty_entry]
            current_terms.append(("", term_used_for_empty))

    def __getTermsForCurrentKey(self):
        terms = self.__currentAppData.peopledata_terms[self.__currentKey]

        if not terms:
            terms = []

        self.__updateTermsFromData(self.__currentKey, terms)

        return terms