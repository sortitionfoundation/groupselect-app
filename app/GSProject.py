"""The app's project model, holding participants' data and allocation state."""

from pathlib import Path

import pandas as pd

from groupselect import Algorithm

from GSAppFieldMode import GSAppFieldMode
from GSSetup import GSSetup, next_unique_name
from base_app.AbstractProject import AbstractProject
from importing.DataImportHandle import DataImportHandle


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
    """The state of a GroupSelect project: participants, settings, results."""

    def __init__(
        self,
        output_dir: None | Path = None,
        data_handle: None | DataImportHandle = None,
        terms: None | dict = None,
        fields_usage: None | dict[GSAppFieldMode, list[int]] = None,
        manuals: None | dict[int, int] = None,
        settings: None | dict = None,
        setups: None | list[GSSetup] = None,
        selected_setup: None | int = None,
        selected_allocation: None | int = None,
        pareto_probs: None | dict[int, float] = None,
    ):
        """Initialise the project, defaulting any values not provided."""
        super(GSProject, self).__init__(output_dir=output_dir)
        self.data_handle: None | DataImportHandle = data_handle
        self.terms: dict = terms or {}
        self.fields_usage: dict[GSAppFieldMode, list[int]] = fields_usage or {
            usage_mode: [] for usage_mode in GSAppFieldMode
        }
        self.manuals: dict[int, int] = manuals or {}
        self.settings: dict = settings or settings_template.copy()

        # Computed results: a list of named "Setups" (ensembles), each
        # holding a list of named allocations ("rounds"). `selected_setup`/
        # `selected_allocation` track which node is currently shown in the
        # Results tab -- `selected_allocation is None` (with `selected_setup`
        # set) means the whole setup's summary is selected, rather than one
        # specific allocation within it.
        self.setups: list[GSSetup] = setups or []
        self.selected_setup: None | int = selected_setup
        self.selected_allocation: None | int = selected_allocation

        self._pdata_mapped: None | pd.DataFrame = None

    @property
    def pdata(self) -> None | pd.DataFrame:
        """The imported participants' data, or None if none is imported."""
        return self.data_handle.imported_data if self.data_handle else None

    @property
    def pdata_mapped(self) -> None | pd.DataFrame:
        """The participants' data with term mappings applied, cached."""
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
        """Invalidate the cached, term-mapped participants' data."""
        self._pdata_mapped = None

    def next_setup_name(self) -> str:
        """Return the next default "Setup #" name, unique in the project."""
        return next_unique_name("Setup", [setup.name for setup in self.setups])

    def fields_display(self) -> list[str]:
        """Return field IDs to display, in diversify/cluster/keep modes."""
        return [
            field_id
            for field_usage, field_ids in self.fields_usage.items()
            for field_id in field_ids
            if field_usage
            in [
                GSAppFieldMode.Diversify,
                GSAppFieldMode.Cluster,
                GSAppFieldMode.Keep,
            ]
        ]
