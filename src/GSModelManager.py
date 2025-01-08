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
    def _setup_models(self) -> dict[str, AbstractProjectModel]:
        return {
            'pdata': GSParticipantsDataModel(),
            'pfields': GSParticipantsFieldsModel(),
            'pterms': GSParticipantsTermsModel(),
            'almanuals': GSManualsListModel(),
            'alsettings': GSAllocationSettingsModel(),
            'results_list': GSResultsListModel(),
            'results_table': GSResultsTableModel(),
        } | {
            f"fu{usage_mode.name.lower()}": GSFieldUsageListModel(usage_mode)
            for usage_mode in GSAppFieldMode
        }

    def updated_participants(self):
        self._ctx.project_manager.project.clear_cache_mapped()

        self._models['pdata'].layoutChanged.emit()
        self._models['pfields'].layoutChanged.emit()
        self._models['pterms'].updated_pdata()
        for usage_mode in GSAppFieldMode:
            self._models[f"fu{usage_mode.name.lower()}"].updated_fields()

    def updated_results(self):
        self._models['results_list'].updated_results()
        self._models['results_table'].updated_results()
