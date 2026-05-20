from pathlib import Path

import pandas as pd
from base_app.AbstractProject import AbstractProject
from groupselect import Algorithm, AllocationEnsemble
from GSAppFieldMode import GSAppFieldMode
from importing.GSDataImportHandle import GSDataImportHandle

settings_template = {
    "n_part_per_group": 8,
    "n_allocations": 3,
    "n_attempts": 100,
    "seed": 0,
    "algorithm": Algorithm.HERMES.name,
    "pareto_probs": {},
    "cluster_val": 0,
}
settings_lookup = list(settings_template)


class GSProject(AbstractProject):
    """Mutable state container for one GroupSelect project.

    Persisted to a ``.gspr`` file.  All UI components access project
    data through the :class:`AppContext`'s ``project_manager``.

    Attributes:
        data_handle: Manages the imported participant file.  Provides
            the raw DataFrame via ``imported_data`` and the column-name
            mapping via ``column_naming``.
        terms: ``{col_id: [(raw_value, display_label), ...]}`` used to
            substitute raw field values with human-readable labels before
            running the allocation.
        fields_usage: ``{GSAppFieldMode: [col_id, ...]}`` assigning each
            imported column to a usage role.
        manuals: ``{participant_row_index: group_index}`` forced
            participant-to-group pre-assignments.
        settings: Algorithm configuration dict.  Keys: ``n_part_per_group``,
            ``n_allocations``, ``n_attempts``, ``seed``, ``algorithm``
            (str name), ``pareto_probs`` (``{field_id: float}``).
        results: Accumulated :class:`~groupselect.AllocationEnsemble`
            containing all allocations generated in this session.
        result_current: Index of the currently selected allocation in the
            Results tab, or ``None``.
    """

    def __init__(
        self,
        output_dir: None | Path = None,
        data_handle: None | GSDataImportHandle = None,
        terms: None | dict = None,
        fields_usage: None | dict[GSAppFieldMode, list[int]] = None,
        manuals: None | dict[int, int] = None,
        settings: None | dict = None,
        results: None | AllocationEnsemble = None,
        result_current: None | int = None,
        pareto_probs: None | dict[int, float] = None,
    ):
        super(GSProject, self).__init__(output_dir=output_dir)
        self.data_handle: None | GSDataImportHandle = data_handle
        self.terms: dict = terms or {}
        self.fields_usage: dict[GSAppFieldMode, list[int]] = fields_usage or {
            usage_mode: [] for usage_mode in GSAppFieldMode
        }
        self.manuals: dict[int, int] = manuals or {}
        self.settings: dict = settings or settings_template.copy()
        self.results: AllocationEnsemble = results or AllocationEnsemble()
        self.result_current: None | int = result_current

        self._pdata_mapped: None | pd.DataFrame = None

    @property
    def pdata(self) -> None | pd.DataFrame:
        return self.data_handle.imported_data if self.data_handle else None

    @property
    def pdata_mapped(self) -> None | pd.DataFrame:
        # Return None if participants' data is not set.
        if self.pdata is None:
            return None

        # Return mapped participants' data from cache if it exists.
        if self._pdata_mapped is not None:
            return self._pdata_mapped

        # Generate mapped participants' data, save to cache, and return.
        pdata = self.pdata.copy()
        for col_id, col_terms in self.terms.items():
            if col_id in pdata:
                pdata[col_id] = pdata[col_id].map(dict(col_terms))
        self._pdata_mapped = pdata
        return pdata

    def clear_cache_mapped(self):
        self._pdata_mapped = None

    def fields_display(self) -> list[str]:
        """Return the column IDs whose values should be shown in results.

        Includes ``Diversify``, ``Cluster``, and ``Display`` fields.
        """
        return [
            field_id
            for field_usage, field_ids in self.fields_usage.items()
            for field_id in field_ids
            if field_usage
            in [
                GSAppFieldMode.Diversify,
                GSAppFieldMode.Cluster,
                GSAppFieldMode.Display,
            ]
        ]
