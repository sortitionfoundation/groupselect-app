from PySide6.QtWidgets import QWidget, QTabWidget, QVBoxLayout

from base_app.AbstractMainWindow import AbstractMainWindow
from base_app.AppContext import AppContext

from participants.GSParticipantsTab import GSParticipantsTab
from generate.GSGenerateTab import GSGenerateTab
from results.GSResultsTab import GSResultsTab


class GSMainTabs(QWidget):
    def __init__(self, ctx: AppContext, main_window: AbstractMainWindow):
        super(GSMainTabs, self).__init__(parent=main_window)
        self._ctx = ctx

        self._create_ui()

    def _create_ui(self):
        self._tab_participants = GSParticipantsTab(self._ctx)
        self._tab_generate = GSGenerateTab(self._ctx)
        self._tab_results = GSResultsTab(self._ctx)

        self._tabs = QTabWidget()
        self._tabs.addTab(self._tab_participants, '&Participants')
        self._tabs.addTab(self._tab_generate, '&Generate')
        self._tabs.addTab(self._tab_results, '&Results')
        self._tabs.currentChanged.connect(self._main_tabs_switched)

        m = 10
        layout = QVBoxLayout(self)
        layout.setContentsMargins(m, m, m, m)
        layout.addWidget(self._tabs)
        self.setLayout(layout)

    def project_opened(self):
        self._tabs.setCurrentIndex(0)

    def _main_tabs_switched(self, index):
        if index == 1:
            self._tab_generate.update_groups_estimate()
