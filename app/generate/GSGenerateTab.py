from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QGridLayout

from generate.GSGenerateFieldsGroup import GSGenerateFieldsGroup
from generate.GSGenerateSettingsGroup import GSGenerateSettingsGroup

if TYPE_CHECKING:
    from base_app.AppContext import AppContext


class GSGenerateTab(QWidget):
    _ctx: 'AppContext'

    def __init__(self, ctx: 'AppContext'):
        super(GSGenerateTab, self).__init__()
        self._ctx = ctx

        self._create_ui()

    def _create_ui(self):
        self._group_fields = GSGenerateFieldsGroup(self._ctx)
        self._group_settings = GSGenerateSettingsGroup(self._ctx)

        layout = QGridLayout()
        layout.addWidget(self._group_fields, 0, 0)
        layout.addWidget(self._group_settings, 1, 0)
        layout.setRowStretch(0, 1)
        self.setLayout(layout)

    def update_groups_estimate(self):
        self._group_settings.update_groups_estimate()