"""List model of the manually-fixed participant-to-group assignments."""

from math import ceil

from PySide6 import QtCore
from PySide6.QtCore import Qt, QModelIndex, QPersistentModelIndex

from base_app.AbstractProjectModel import AbstractProjectModel

from GSAppFieldMode import GSAppFieldMode
from GSProject import GSProject


class GSManualsListModel(QtCore.QAbstractListModel, AbstractProjectModel):
    """List of manual participant-to-group assignments, shown by label."""

    _project: GSProject

    # project updated
    def updated_project(self, project: GSProject):
        """Bind the model to a (newly opened) project."""
        self._project = project
        self.layoutChanged.emit()

    def updated_manuals(self):
        """Notify the view that the manual assignments changed."""
        self.layoutChanged.emit()

    def data(
        self, index: QModelIndex | QPersistentModelIndex, role: int = ...
    ):
        """Return the display label for a manual assignment."""
        if (
            index.isValid()
            and index.row() <= self.rowCount(None)
            and role == Qt.ItemDataRole.DisplayRole
        ):
            p_id = list(self._project.manuals)[index.row()]
            g_id = self._project.manuals[p_id]

            label_fields = self._project.fields_usage[GSAppFieldMode.Label]
            p_label = (
                " ".join(self._project.pdata.loc[p_id, label_fields])
                + f" ({p_id})"
                if label_fields
                else str(p_id)
            )

            return f"{p_label}: Group {g_id + 1}"

        return None

    def rowCount(
        self, parent: QModelIndex | QPersistentModelIndex = ...
    ) -> int:
        """Return the number of manual assignments."""
        if self._project is None:
            return 0
        return len(self._project.manuals)

    def get_allocatables(self) -> dict[int, str]:
        """Return the participants not yet manually assigned, by label."""
        label_fields = self._project.fields_usage[GSAppFieldMode.Label]
        allocatables = self._project.pdata.loc[
            ~self._project.pdata.index.isin(self._project.manuals)
        ]
        if label_fields:
            labels = allocatables.filter(label_fields).apply(" ".join, axis=1)
            return {
                p_id: f"{p_label} ({p_id})" for p_id, p_label in labels.items()
            }
        else:
            return {p_id: str(p_id) for p_id in allocatables.index}

    def get_groups(self) -> dict[int, str]:
        """Return the available group labels, by group index."""
        n_groups = ceil(
            len(self._project.pdata)
            / self._project.settings["n_part_per_group"]
        )
        return {g_id: f"Group {g_id + 1}" for g_id in range(n_groups)}

    def add_manual(self, p_id: int | str, g_id: int):
        """Assign participant `p_id` to group `g_id`."""
        self._project.manuals[p_id] = g_id
        self.layoutChanged.emit()

    def remove_manual(self, row_id: int):
        """Remove the manual assignment at the given row."""
        del self._project.manuals[list(self._project.manuals)[row_id]]
        self.layoutChanged.emit()
