"""Subtab for editing field names and their term mappings."""

from PySide6.QtWidgets import (
    QWidget,
    QHeaderView,
    QHBoxLayout,
    QListView,
    QTableView,
)

from base_app.AppContext import AppContext


class GSParticipantsFieldsSubtab(QWidget):
    """Field list next to a terms table for the currently selected field."""

    def __init__(self, ctx: "AppContext"):
        """Initialise the subtab and build the field list and terms table."""
        super(GSParticipantsFieldsSubtab, self).__init__()
        self._ctx = ctx

        self._create_ui()

    def _create_ui(self):
        self.fields_list = QListView()
        self.fields_list.setModel(self._ctx.model_manager["pfields"])
        self.fields_list.setToolTip(
            "Imported data columns. Select a field to view and edit its "
            "term mapping on the right."
        )
        self.fields_list.selectionModel().currentChanged.connect(
            self.fieldlist_select
        )

        self.terms_table = QTableView()
        self.terms_table.setModel(self._ctx.model_manager["pterms"])
        self.terms_table.setToolTip(
            "Normalise the raw values found in the selected field by "
            "mapping them to a common term, e.g. mapping both \"M\" and "
            "\"Male\" to \"Male\"."
        )
        self.terms_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.terms_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.fields_list)
        layout.addWidget(self.terms_table)
        self.setLayout(layout)

        self.termslist_disable()

    def termslist_enable(self):
        """Enable the terms table."""
        self.terms_table.setDisabled(False)

    def termslist_disable(self):
        """Disable the terms table."""
        self.terms_table.setDisabled(True)

    def fieldlist_select(self, current):
        """Show the terms of the newly selected field."""
        self.termslist_enable()
        self._ctx.model_manager["pterms"].update_key(current.row())

    def clear(self):
        """Deselect the field list and disable the terms table."""
        self.fields_list.clearSelection()
        self._ctx.model_manager["pterms"].update_key(None)
