from typing import TYPE_CHECKING

from PySide6.QtWidgets import QTabWidget

from participants.GSParticipantsDataSubtab import GSParticipantsDataSubtab
from participants.GSParticipantsFieldsSubtab import GSParticipantsFieldsSubtab

if TYPE_CHECKING:
    from base_app.AppContext import AppContext


class GSParticipantsTab(QTabWidget):
    _ctx: 'AppContext'

    def __init__(self, ctx: 'AppContext'):
        super(GSParticipantsTab, self).__init__()
        self._ctx = ctx

        self._create_ui()

    def _create_ui(self):
        subtab_data = GSParticipantsDataSubtab(self._ctx)
        subtab_fields = GSParticipantsFieldsSubtab(self._ctx)

        self.setTabPosition(QTabWidget.TabPosition.South)
        self.addTab(subtab_data, 'Data')
        self.addTab(subtab_fields, 'Fields')
