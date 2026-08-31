"""The Generate tab: field settings, manual allocations, settings."""

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QGridLayout

from generate.GSGenerateFieldsGroup import GSGenerateFieldsGroup
from generate.GSManualAllocationsGroup import GSManualAllocationsGroup
from generate.GSGenerateSettingsGroup import GSGenerateSettingsGroup

if TYPE_CHECKING:
    from base_app.AppContext import AppContext


class GSGenerateTab(QWidget):
    """Tab for configuring fields and settings, then running an allocation."""

    _ctx: "AppContext"

    def __init__(self, ctx: "AppContext"):
        """Initialise the tab and build the field/manual/settings groups."""
        super(GSGenerateTab, self).__init__()
        self._ctx = ctx

        self._create_ui()

    def _create_ui(self):
        self._group_fields = GSGenerateFieldsGroup(self._ctx)
        self._group_manuals = GSManualAllocationsGroup(self._ctx)
        self._group_settings = GSGenerateSettingsGroup(self._ctx)

        layout = QGridLayout()
        layout.addWidget(self._group_fields, 0, 0, 1, 2)
        layout.addWidget(self._group_manuals, 1, 0)
        layout.addWidget(self._group_settings, 1, 1)
        layout.setRowStretch(0, 1)
        layout.setColumnStretch(0, 3)
        layout.setColumnStretch(1, 2)
        self.setLayout(layout)

    def update_groups_estimate(self):
        """Forward the request to refresh the estimated number of groups."""
        self._group_settings.update_groups_estimate()
