"""Table view for the summary of one setup's allocations."""

from PySide6.QtWidgets import QWidget, QTableView, QHeaderView


class GSSetupSummaryTableView(QTableView):
    """Table view showing population and per-allocation statistics."""

    def __init__(self, parent: QWidget | None = None):
        """Initialise the view with word-wrapped, auto-sized cells."""
        super(GSSetupSummaryTableView, self).__init__(parent=parent)
        self.setToolTip(
            "Summary across all rounds of the selected setup: population "
            "and diversity/meeting statistics."
        )
        self.setWordWrap(True)
        self.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )

    def setModel(self, model):
        """Set the model and keep row heights fitted to wrapped content."""
        super(GSSetupSummaryTableView, self).setModel(model)
        model.layoutChanged.connect(self.resizeRowsToContents)
        self.resizeRowsToContents()
