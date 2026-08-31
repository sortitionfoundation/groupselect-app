"""Persisted "Export as.../Export" configuration and component selection."""


class GSExportSelection:
    """Which components are included in an export.

    `all_results=True` means every setup and allocation -- present *and*
    any added later -- is included, matching the "All" node in the export
    dialog's tree being fully checked. Otherwise, `setups` maps each
    included setup's `setup_id` to one of:
    - `"all"`: that setup as a whole -- its own summary, plus every one of
      its allocations, present and any added later;
    - `"summary_only"`: just that setup's own summary (only reachable via a
      CSV export, which can only ever hold one table);
    - a `set` of specific `allocation_id`s: only those particular
      allocations, never auto-extended by ones added later.

    A setup not present as a key in `setups` (and not covered by
    `all_results`) is excluded entirely.
    """

    def __init__(
        self,
        raw_data: bool = False,
        mapped_data: bool = False,
        terminology: bool = False,
        all_results: bool = False,
        setups: None | dict[int, str | set[int]] = None,
    ):
        """Initialise the selection, defaulting to nothing selected."""
        self.raw_data: bool = raw_data
        self.mapped_data: bool = mapped_data
        self.terminology: bool = terminology
        self.all_results: bool = all_results
        self.setups: dict[int, str | set[int]] = (
            setups if setups is not None else {}
        )

    def is_empty(self) -> bool:
        """Return whether nothing at all is selected."""
        return not (
            self.raw_data
            or self.mapped_data
            or self.terminology
            or self.all_results
            or self.setups
        )


class GSExportSettings:
    """A full "Export as..." configuration: format, options, and selection.

    Stored as `GSProject.export_settings` after a successful "Export as...",
    so a later plain "Export" can repeat it without re-prompting.
    """

    def __init__(
        self,
        file_path: str,
        file_format: str,
        csv_sep: str = ";",
        csv_quote: str = '"',
        selection: None | GSExportSelection = None,
    ):
        """Initialise the settings, defaulting the selection if not given."""
        self.file_path: str = file_path
        self.file_format: str = file_format
        self.csv_sep: str = csv_sep
        self.csv_quote: str = csv_quote
        self.selection: GSExportSelection = (
            selection if selection is not None else GSExportSelection()
        )
