"""The main tab widget hosting the participants, generate, and results tabs."""

from PySide6.QtWidgets import QWidget, QTabWidget, QVBoxLayout

from base_app.AbstractMainWindow import AbstractMainWindow
from base_app.AppContext import AppContext

from participants.GSParticipantsTab import GSParticipantsTab
from generate.GSGenerateTab import GSGenerateTab
from results.GSResultsTab import GSResultsTab


class GSMainTabs(QWidget):
    """The central widget holding the participants, generate & results tabs."""

    def __init__(self, ctx: AppContext, main_window: AbstractMainWindow):
        """Initialise the tab widget and build the child tabs."""
        super(GSMainTabs, self).__init__(parent=main_window)
        self._ctx = ctx

        self._create_ui()

    def _create_ui(self):
        self._tab_participants = GSParticipantsTab(self._ctx)
        self._tab_generate = GSGenerateTab(self._ctx)
        self._tab_results = GSResultsTab(self._ctx)

        self._tabs = QTabWidget()
        self._tabs.addTab(self._tab_participants, "&Participants")
        self._tabs.setTabToolTip(0, "Import and inspect participants' data.")
        self._tabs.addTab(self._tab_generate, "&Generate")
        self._tabs.setTabToolTip(
            1, "Configure fields and settings, then generate allocations."
        )
        self._tabs.addTab(self._tab_results, "&Results")
        self._tabs.setTabToolTip(
            2, "Inspect, edit, rename, and delete generated allocations."
        )
        self._tabs.currentChanged.connect(self._main_tabs_switched)

        m = 10
        layout = QVBoxLayout(self)
        layout.setContentsMargins(m, m, m, m)
        layout.addWidget(self._tabs)
        self.setLayout(layout)

    def project_opened(self):
        """Reset the tab selection to the Participants tab."""
        self._tabs.setCurrentIndex(0)

    def _main_tabs_switched(self, index):
        if index == 1:
            self._tab_generate.update_groups_estimate()
        elif index == 2:
            self._tab_results.refresh_selection()
