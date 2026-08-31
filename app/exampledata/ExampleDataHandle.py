"""Data handles that load example data instead of an imported file."""

from pathlib import Path

import pandas as pd

from groupselect.examples import generate_participants


class ExampleDataHandle:
    """A stand-in for `DataImportHandle`, loading example data on the spot.

    Exposes the same `title` / `imported_data` / `column_naming` /
    `import_data()` interface as `DataImportHandle`, so it can be
    dropped straight into `GSProject.data_handle` and used by the rest
    of the app unchanged. Unlike a real import there is no source file
    to preview or configure columns for -- `_build()` already returns
    the data with its final column names, so it can be loaded directly,
    without going through the import dialogue.
    """

    def __init__(self, title: str):
        """Initialise the handle and load its data for the first time."""
        self._title: str = title
        self._imported: None | pd.DataFrame = None
        self._column_naming: dict[int, str] = {}
        self.import_data()

    @property
    def title(self) -> str:
        """A short label identifying this example dataset."""
        return self._title

    @property
    def column_naming(self) -> dict[int, str]:
        """The mapping from column index to column name, for used columns."""
        return self._column_naming

    def update_column_naming(self, column_naming_updated: dict[int, str]):
        """Replace the column-index-to-name mapping."""
        self._column_naming = column_naming_updated

    @property
    def imported_data(self) -> None | pd.DataFrame:
        """The loaded example data."""
        return self._imported

    def import_data(self):
        """(Re-)build the data set from its source.

        Called once when the handle is created, and again whenever the
        user picks "Update import" -- for a predefined dataset that just
        re-reads the same CSV; for a synthetic one it draws a fresh
        random sample.
        """
        df = self._build().astype(str)
        names = list(df.columns)
        df.columns = range(len(names))
        # Match `datahandling.DataHandle.read()`, whose rows are numbered
        # from 1 -- this is also what's shown as the participant's row ID
        # placeholder (manuals dialogue, results table) when no Label
        # field is set, so it must agree with a real file import's index.
        df.index += 1
        self._imported = df
        self._column_naming = dict(enumerate(names))

    def _build(self) -> pd.DataFrame:
        """Return the example data as a DataFrame with real column names."""
        raise NotImplementedError


class PredefinedExampleDataHandle(ExampleDataHandle):
    """Loads one of the example CSV files bundled with groupselect."""

    def __init__(self, csv_path: Path):
        """Initialise the handle to load `csv_path` (kept for re-import)."""
        self._csv_path = csv_path
        super(PredefinedExampleDataHandle, self).__init__(
            title=f"Example data: {csv_path.name}"
        )

    def _build(self) -> pd.DataFrame:
        return pd.read_csv(self._csv_path, dtype=str)


class SyntheticExampleDataHandle(ExampleDataHandle):
    """Generates a fresh, random synthetic dataset of a given size.

    Always creates 12 diversity fields -- three each with 2, 3, 4 and 5
    features -- named "Field A" .. "Field L", with feature values named
    "Feature A1", "Feature A2", etc. A first column, "Participant",
    holds a running "Person 1", "Person 2", ... label. A new random
    sample is drawn every time, including via "Update import".
    """

    # Three fields each with 2, 3, 4 and 5 features -- 12 fields total.
    _FIELD_FEATURE_COUNTS = [2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5]

    def __init__(self, n_participants: int):
        """Initialise the handle to generate `n_participants` rows."""
        self._n_participants = n_participants
        super(SyntheticExampleDataHandle, self).__init__(
            title=f"Synthetic dataset ({n_participants} participants)"
        )

    def _build(self) -> pd.DataFrame:
        codes = generate_participants(
            n_participants=self._n_participants,
            n_div_fields=len(self._FIELD_FEATURE_COUNTS),
            n_field_features=self._FIELD_FEATURE_COUNTS,
        )
        letters = [
            chr(ord("A") + field_index)
            for field_index in range(len(self._FIELD_FEATURE_COUNTS))
        ]

        data = {
            "Participant": [
                f"Person {i + 1}" for i in range(self._n_participants)
            ]
        }
        for letter, column in zip(letters, codes.T):
            data[f"Field {letter}"] = [
                f"Feature {letter}{code + 1}" for code in column
            ]

        return pd.DataFrame(data)
