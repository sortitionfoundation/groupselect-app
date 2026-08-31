"""The app's project model, holding participants' data and allocation state."""

import copy
from pathlib import Path

import pandas as pd

from groupselect import Algorithm

from GSAppFieldMode import GSAppFieldMode
from GSExportSettings import GSExportSettings
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
    "pareto_prob": 0.5,
    "swap_rounds": 1,
    "cluster_tables": 2,
}
settings_lookup = list(settings_template)

# Which allocation settings each algorithm actually reads (derived from the
# keyword arguments each `groupselect.algorithms.algorithm_*` function
# accepts, beyond the participants/fields/groups/manuals/progress_func that
# every algorithm takes regardless). Used to grey out settings that have no
# effect on the currently chosen algorithm, in both the advanced-settings
# dialog and the main allocation settings form.
ALGORITHM_SETTINGS: dict[Algorithm, set[str]] = {
    Algorithm.Legacy: {"n_attempts", "seed"},
    Algorithm.DREAM: {"seed", "pareto_prob", "swap_rounds", "cluster_tables"},
    Algorithm.HERMES: {
        "seed",
        "pareto_probs",
        "swap_rounds",
        "cluster_tables",
    },
}


class GSProject(AbstractProject):
    """The state of a GroupSelect project: participants, settings, results."""

    # Bump this whenever a change to this class's data shape needs a
    # migration to stay readable in an older `.gspr` file -- a field renamed,
    # restructured, or removed with no safe default (a field merely *added*
    # usually doesn't need one; see the `settings.setdefault()` loop below,
    # which already backfills newly-added `settings` keys for old files).
    # Register the corresponding step in `migrations()` in the same change
    # that bumps this. See `base_app.AbstractProject.migrations` for how a
    # migration function is written and what it receives.
    SCHEMA_VERSION = 1

    @classmethod
    def migrations(cls) -> dict:
        """Map `{from_version: migrate}` upgrading old `.gspr` file data.

        Empty for now -- no released version of GroupSelect has needed one
        yet. Add an entry each time `SCHEMA_VERSION` above is bumped, e.g.::

            @classmethod
            def migrations(cls):
                def _v1_to_v2(data):
                    data["new_field"] = data.pop("old_field")
                    return data
                return {1: _v1_to_v2}
        """
        return {}

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
        export_settings: None | GSExportSettings = None,
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
        # `settings_template` holds nested mutable defaults (e.g.
        # `pareto_probs`), so a plain `.copy()` would shallow-copy those and
        # let mutations on one project's settings leak into the template
        # (and thus into every other project created afterwards) -- use a
        # deep copy instead. Likewise, a project loaded from an older save
        # file may predate settings added since (e.g. `swap_rounds`); fill
        # those in from the template rather than letting lookups of them
        # raise `KeyError`.
        self.settings: dict = settings or copy.deepcopy(settings_template)
        for key, default in settings_template.items():
            self.settings.setdefault(key, copy.deepcopy(default))

        # Computed results: a list of named "Setups" (ensembles), each
        # holding a list of named allocations ("rounds"). `selected_setup`/
        # `selected_allocation` track which node is currently shown in the
        # Results tab -- `selected_allocation is None` (with `selected_setup`
        # set) means the whole setup's summary is selected, rather than one
        # specific allocation within it.
        self.setups: list[GSSetup] = setups or []
        self.selected_setup: None | int = selected_setup
        self.selected_allocation: None | int = selected_allocation

        # The last successful "Export as..." configuration, if any -- lets
        # "Export" repeat it without re-prompting. `_next_id` hands out the
        # stable `setup_id`/allocation ids used to track "the same setup/
        # allocation" across separate exports, surviving renames/reorders.
        self.export_settings: None | GSExportSettings = export_settings
        self._next_id: int = 1

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

    def next_id(self) -> int:
        """Return a fresh, project-unique ID for a new setup/allocation."""
        id_ = self._next_id
        self._next_id += 1
        return id_

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
