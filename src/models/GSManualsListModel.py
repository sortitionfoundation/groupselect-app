from PySide6 import QtCore
from PySide6.QtCore import Qt, QModelIndex, QPersistentModelIndex

from base_app.AbstractProjectModel import AbstractProjectModel

from groupselect import FieldMode

from GSProject import GSProject


class GSManualsListModel(QtCore.QAbstractListModel, AbstractProjectModel):
    _project: GSProject

    # project updated
    def updated_project(self, project: GSProject):
        self._project = project
        self.layoutChanged.emit()

    def updated_manuals(self):
        self.layoutChanged.emit()

    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = ...):
        if index.isValid() and index.row() <= self.rowCount(None) and role == Qt.ItemDataRole.DisplayRole:
            p_id = list(self._project.manuals)[index.row()]
            g_id = self._project.manuals[p_id]

            print_fields = self._project.fields_usage[FieldMode.Print]
            p_label = (
                ' '.join(self._project.pdata.loc[p_id, print_fields])
                if print_fields else
                p_id
            )

            return f"{p_label}: Group {g_id+1}"

        return None

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = ...) -> int:
        if self._project is None:
            return 0
        return len(self._project.manuals)

    def get_allocatables(self) -> dict[int, str]:
        print_fields = self._project.fields_usage[FieldMode.Print]
        allocatables = self._project.pdata.loc[~self._project.pdata.index.isin(self._project.manuals)]
        return (
            allocatables.filter(print_fields)
                .apply(' '.join, axis=1)
                .to_dict()
            if print_fields else
            allocatables.filter(print_fields)
        )

    def get_groups(self) -> dict[int, str]:
        return {
            g_id: f"Group {g_id+1}"
            for g_id in range(self._project.settings['n_groups'])
        }

    def add_manual(self, p_id: int | str, g_id: int):
        self._project.manuals[p_id] = g_id
        self.layoutChanged.emit()

    def remove_manual(self, row_id: int):
        del self._project.manuals[list(self._project.manuals)[row_id]]
        self.layoutChanged.emit()
