"""The app's model manager, wiring up all Qt models used across the tabs."""

from base_app.AbstractModelManager import AbstractModelManager
from base_app.AbstractProjectModel import AbstractProjectModel

from GSAppFieldMode import GSAppFieldMode
from models.GSAllocationSettingsModel import GSAllocationSettingsModel
from models.GSFieldUsageListModel import GSFieldUsageListModel
from models.GSManualsListModel import GSManualsListModel
from models.GSParticipantsFieldsModel import GSParticipantsFieldsModel
from models.GSParticipantsDataModel import GSParticipantsDataModel
from models.GSParticipantsTermsModel import GSParticipantsTermsModel
from models.GSResultsTreeModel import GSResultsTreeModel
from models.GSResultsTableModel import GSResultsTableModel
from models.GSSetupSummaryTableModel import GSSetupSummaryTableModel


class GSModelManager(AbstractModelManager):
    """Creates and manages all Qt models used by the app's widgets."""

    def _setup_models(self) -> dict[str, AbstractProjectModel]:
        models = {
            "pdata": GSParticipantsDataModel(),
            "pfields": GSParticipantsFieldsModel(),
            "pterms": GSParticipantsTermsModel(),
            "almanuals": GSManualsListModel(),
            "alsettings": GSAllocationSettingsModel(),
            "results_tree": GSResultsTreeModel(),
            "results_table": GSResultsTableModel(),
            "results_summary": GSSetupSummaryTableModel(),
        } | {
            f"fu{usage_mode.name.lower()}": GSFieldUsageListModel(usage_mode)
            for usage_mode in GSAppFieldMode
        }

        # The manual-allocation list displays participants using whichever
        # field(s) are currently marked as "Label", so it must refresh
        # whenever that field usage changes (drag-and-drop between the
        # field-usage lists) or the underlying participants' data changes
        # (which also runs through fulabel's updated_fields(), see
        # updated_participants below).
        models["fulabel"].layoutChanged.connect(
            models["almanuals"].updated_manuals
        )

        return models

    def updated_participants(self):
        """Refresh all models that depend on the participants' data."""
        self._ctx.project_manager.project.clear_cache_mapped()

        self._models["pdata"].layoutChanged.emit()
        self._models["pfields"].layoutChanged.emit()
        self._models["pterms"].updated_pdata()
        for usage_mode in GSAppFieldMode:
            self._models[f"fu{usage_mode.name.lower()}"].updated_fields()

    def updated_results(self):
        """Refresh the models that display the allocation results."""
        self._models["results_tree"].updated_results()
        self._models["results_table"].updated_results()
        self._models["results_summary"].updated_results()
