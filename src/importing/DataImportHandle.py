import pandas as pd
from pathlib import Path

from datahandling import DataHandle


class DataImportHandle(DataHandle):
    _imported: None | pd.DataFrame
    _column_naming: dict[int, str]

    def __init__(self, file_path: Path, file_type: str):
        super(DataImportHandle, self).__init__(file_path, file_type)
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
        # sort column mapping
        col_mapping_sorted = dict(sorted(self._column_naming.items()))

        # add extract-specific keywords to file_config
        file_config = {
            'skiprows': self._file_config['first'] - 1 if self._file_config['first'] is not None else 0,
            'nrows': (
                (self._file_config['last'] - self._file_config['first'] + 1)
                if not (self._file_config['first'] is None or self._file_config['last'] is None) else
                None
            ),
            'usecols': list(col_mapping_sorted.keys()),
            # Column names will not be added to dataframe but determined by GUI from dataframe directly.
            # 'names': [
            #     col_name or excel_col_name(col_id)
            #     for col_id, col_name in col_mapping_sorted.items()
            # ],
            'dtype': 'str',
        }

        # call read function
        self._imported = self.read(file_config=file_config)
