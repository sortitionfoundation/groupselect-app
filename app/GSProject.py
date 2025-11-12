from pathlib import Path

import pandas as pd

from groupselect import AllocationEnsemble

from GSAppFieldMode import GSAppFieldMode
from base_app.AbstractProject import AbstractProject
from importing.DataImportHandle import DataImportHandle


settings_template = {
    'n_part_per_group': 8,
    'n_allocations': 3,
    'n_attempts': 100,
    'seed': 0,
}
settings_lookup = list(settings_template)


class GSProject(AbstractProject):
    data_handle: None | DataImportHandle
    terms: dict
    fields_usage: dict[GSAppFieldMode, list[int]]
    manuals: dict[int, int]
    settings: dict
    results: list[list]
    result_current: None | int

    _pdata_mapped: None | pd.DataFrame

    def __init__(self,
                 output_dir: None | Path = None,
                 data_handle: None | DataImportHandle = None,
                 terms: None | dict = None,
                 fields_usage: None | dict[GSAppFieldMode, list[int]] = None,
                 manuals: None | dict[int, int] = None,
                 settings: None | dict = None,
                 results: None | list[list] = None,
                 result_current: None | int = None):
        super(GSProject, self).__init__(output_dir=output_dir)
        self.data_handle = data_handle
        self.terms = terms or {}
        self.fields_usage = fields_usage or {usage_mode: [] for usage_mode in GSAppFieldMode}
        self.manuals = manuals or {}
        self.settings = settings or settings_template.copy()
        self.results = results or []
        self.result_current = result_current

        self._pdata_mapped = None

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
