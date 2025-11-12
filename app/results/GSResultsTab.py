from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QListView, QGridLayout

from results.GSResultTableView import GSResultTableView

if TYPE_CHECKING:
    from base_app.AppContext import AppContext


class GSResultsTab(QWidget):
    _ctx: 'AppContext'

    def __init__(self, ctx: 'AppContext'):
        super(GSResultsTab, self).__init__()
        self._ctx = ctx

        self._create_ui()

    def _create_ui(self):
        # List of results (individual allocations) to select from.
        results_list = QListView(parent=self)
        results_list.setModel(self._ctx.model_manager['results_list'])
        results_list.selectionModel().currentChanged.connect(self._ctx.model_manager['results_table'].update_current)

        # Table showing one single allocation.
        results_table = GSResultTableView(parent=self)
        results_table.setModel(self._ctx.model_manager['results_table'])

        layout = QGridLayout()
        layout.addWidget(results_list, 0, 0)
        layout.addWidget(results_table, 0, 1)
        layout.setColumnStretch(1, 10)
        self.setLayout(layout)
