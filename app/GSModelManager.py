from base_app.AbstractModelManager import AbstractModelManager
from base_app.AbstractProjectModel import AbstractProjectModel

from GSAppFieldMode import GSAppFieldMode
from models.GSAllocationSettingsModel import GSAllocationSettingsModel
from models.GSFieldUsageListModel import GSFieldUsageListModel
from models.GSManualsListModel import GSManualsListModel
from models.GSParticipantsFieldsModel import GSParticipantsFieldsModel
from models.GSParticipantsDataModel import GSParticipantsDataModel
from models.GSParticipantsTermsModel import GSParticipantsTermsModel
from models.GSResultsListModel import GSResultsListModel
from models.GSResultsTableModel import GSResultsTableModel


class GSModelManager(AbstractModelManager):
    """Manages all Qt MVC models for the GroupSelect App.

    Models are keyed by short string identifiers and accessed via
    ``ctx.model_manager["key"]``.  Each model is a thin view over
    :class:`GSProject` data that emits Qt signals when the project
    state changes.

    Keys:
        ``"pdata"``: participant data table.
        ``"pfields"``: column list for term-editing selection.
        ``"pterms"``: value-label substitution table.
        ``"almanuals"``: manual allocation list.
        ``"alsettings"``: algorithm settings (QDataWidgetMapper target).
        ``"results_list"``: list of generated allocations.
        ``"results_table"``: table view of one selected allocation.
        ``"fu{mode.name.lower()}"``: drag-drop field-usage list, one per
        :class:`GSAppFieldMode` value.
    """

    def _setup_models(self) -> dict[str, AbstractProjectModel]:
        return {
            "pdata": GSParticipantsDataModel(),
            "pfields": GSParticipantsFieldsModel(),
            "pterms": GSParticipantsTermsModel(),
            "almanuals": GSManualsListModel(),
            "alsettings": GSAllocationSettingsModel(),
            "results_list": GSResultsListModel(),
            "results_table": GSResultsTableModel(),
        } | {
            f"fu{usage_mode.name.lower()}": GSFieldUsageListModel(usage_mode)
            for usage_mode in GSAppFieldMode
        }

    def updated_participants(self):
        """Notify all participant-related models that the data has changed.

        Call after importing or re-importing participant data.
        """
        self._ctx.project_manager.project.clear_cache_mapped()

        self._models["pdata"].layoutChanged.emit()
        self._models["pfields"].layoutChanged.emit()
        self._models["pterms"].updated_pdata()
        for usage_mode in GSAppFieldMode:
            self._models[f"fu{usage_mode.name.lower()}"].updated_fields()

    def updated_results(self):
        """Notify result-related models that new allocations are available.

        Call after appending to ``project.results``.
        """
        self._models["results_list"].updated_results()
        self._models["results_table"].updated_results()
