from pathlib import Path

import pandas as pd
from datahandling import DataHandle


class GSDataImportHandle(DataHandle):
    _imported: None | pd.DataFrame
    _column_naming: dict[int, str]

    def __init__(self, file_path: Path, file_type: str):
        super(GSDataImportHandle, self).__init__(file_path, file_type)
        self._column_naming = {}
        self._imported = None

    @property
    def column_naming(self) -> dict[int, str]:
        return self._column_naming

    def update_column_naming(self, column_naming_updated: dict[int, str]):
        self._column_naming = column_naming_updated

    @property
    def imported_data(self) -> None | pd.DataFrame:
        return self._imported

    def import_data(self):
        # Sort column mapping.
        col_mapping_sorted = dict(sorted(self._column_naming.items()))

        # Add extract-specific keywords to file_config.
        file_config = {
            "skiprows": self._file_config["first"] - 1
            if self._file_config["first"] is not None
            else 0,
            "nrows": (
                (self._file_config["last"] - self._file_config["first"] + 1)
                if not (
                    self._file_config["first"] is None
                    or self._file_config["last"] is None
                )
                else None
            ),
            "usecols": list(col_mapping_sorted.keys()),
            "dtype": "str",
        }

        # Call read function.
        self._imported = self.read(file_config=file_config)
