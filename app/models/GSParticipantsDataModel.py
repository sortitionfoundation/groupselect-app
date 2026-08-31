"""Table model showing the raw imported participants' data."""

from PySide6 import QtCore

from datahandling import excel_col_name
from base_app.AbstractProjectModel import AbstractProjectModel

from GSProject import GSProject


class GSParticipantsDataModel(
    AbstractProjectModel, QtCore.QAbstractTableModel
):
    """Table model over the imported participants' data."""

    _project: GSProject
    _view_mode: bool

    def __init__(self):
        """Initialise the model with view mode enabled by default."""
        super(GSParticipantsDataModel, self).__init__()
        self._view_mode = True

    # project updated
    def updated_project(self, project: GSProject):
        """Bind the model to a (newly opened) project."""
        self._project = project
        self.layoutChanged.emit()

    # change settings for field view
    def update_view_mode(self, view_mode: bool):
        """Toggle view mode and notify the view."""
        self._view_mode = view_mode
        self.layoutChanged.emit()

    # abstract method implementations
    def data(self, index, role):
        """Return the raw cell value for display or editing."""
        if self._project is None or self._project.pdata is None:
            return None

        match role:
            case (
                QtCore.Qt.ItemDataRole.DisplayRole
                | QtCore.Qt.ItemDataRole.EditRole
            ):
                return self._project.pdata.iloc[index.row(), index.column()]
            case _:
                return None

    def rowCount(self, index):
        """Return the number of imported participants."""
        if self._project is None or self._project.pdata is None:
            return 0

        return len(self._project.pdata)

    def columnCount(self, index):
        """Return the number of imported data columns."""
        if self._project is None or self._project.pdata is None:
            return 0

        return len(self._project.pdata.columns)

    def headerData(self, index, orientation, role):
        """Return the column's display name or the participant's row number."""
        if self._project is None or self._project.pdata is None:
            return None

        match role:
            case QtCore.Qt.ItemDataRole.DisplayRole:
                match orientation:
                    case QtCore.Qt.Orientation.Horizontal:
                        col_id = list(
                            self._project.data_handle.column_naming.keys()
                        )[index]
                        return self._project.data_handle.column_naming[
                            col_id
                        ] or excel_col_name(col_id)
                    case QtCore.Qt.Orientation.Vertical:
                        return f"{index + 1}"
                    case _:
                        raise Exception(f"Unknown orientation: {orientation}")
            case _:
                return None

    def flags(self, index):
        """Return the flags marking cells as enabled and selectable."""
        return (
            QtCore.Qt.ItemFlag.ItemIsEnabled
            | QtCore.Qt.ItemFlag.ItemIsSelectable
        )
