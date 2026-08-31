"""Table model summarising one setup's allocations against the population."""

import numpy as np
from PySide6 import QtCore
from PySide6.QtCore import Qt

from groupselect import AllocationEnsemble

from base_app.AbstractProjectModel import AbstractProjectModel

from GSProject import GSProject


class GSSetupSummaryTableModel(
    AbstractProjectModel, QtCore.QAbstractTableModel
):
    """Table with one column per allocation, next to the whole population.

    Row 0 repeats the per-field statistics shown in the single-allocation
    table (`GSResultsTableModel`'s "Total size" row): the population as a
    whole in column 0, then each allocation's own average-across-its-groups
    breakdown in the following columns. Row 1 holds the diversity/meeting
    scores: the ensemble-wide scores in column 0 (meeting score included,
    since it is only meaningful across multiple allocations), and each
    allocation's own diversity score (only) in the following columns.
    """

    _project: GSProject

    def __init__(self):
        """Initialise the model."""
        super(GSSetupSummaryTableModel, self).__init__()

    # project updated
    def updated_project(self, project: GSProject):
        """Bind the model to a (newly opened) project."""
        self._project = project
        self.layoutChanged.emit()

    # Triggered when the project's setups/allocations are updated.
    def updated_results(self):
        """Notify the view that the project's results changed."""
        self.layoutChanged.emit()

    def update_current(self, setup_index: None | int):
        """Switch to displaying the summary of the given setup."""
        self._project.selected_setup = setup_index
        self._project.selected_allocation = None
        self.layoutChanged.emit()

    @property
    def _setup(self):
        """The currently selected setup, or None if none is selected."""
        if (
            self._project is None
            or self._project.selected_setup is None
            # A specific allocation (not the setup as a whole) is selected.
            or self._project.selected_allocation is not None
        ):
            return None
        setup_index = self._project.selected_setup
        if setup_index >= len(self._project.setups):
            return None
        return self._project.setups[setup_index]

    def _combined_block(
        self,
        header: str,
        total: int,
        get_field_values,
        avg_size: float,
        subheader: str,
        show_percent: bool = False,
    ) -> str:
        r"""Build a "<header>:\n<n>\n\n<subheader>\n\n<field>:\n<n> ...".

        `get_field_values(field_id)` returns the (mapped) values of that
        field for the relevant subset of participants, as a pandas Series.
        `show_percent` prefixes each term's line with its share of `total`
        as a percentage, e.g. "49.3% (3.9) Male".
        """
        ret = [f"{header}:\n{total}", subheader]
        per_term_factor = avg_size / total if total else 0.0
        for field_id in self._project.fields_display():
            field_name = self._project.data_handle.column_naming[field_id]
            value_counts = get_field_values(field_id).value_counts()
            if show_percent:
                lines = (
                    f"{term_count / total * 100:.1f}% "
                    f"({term_count * per_term_factor:.1f}) {term_name}"
                    for (term_name, term_count) in value_counts.items()
                )
            else:
                lines = (
                    f"{term_count * per_term_factor:.1f} {term_name}"
                    for (term_name, term_count) in value_counts.items()
                )
            ret.append(f"{field_name}:\n" + "\n".join(lines))
        return "\n\n".join(ret)

    def data(self, index, role: int = ...):
        """Return the population/allocation stats or metrics block."""
        if self._setup is None or role != Qt.ItemDataRole.DisplayRole:
            return None

        setup = self._setup
        pdata_mapped = self._project.pdata_mapped

        if index.row() == 0:
            # Statistics row: the population, then one column per
            # allocation.
            if index.column() == 0:
                total = len(pdata_mapped)
                avg_n_groups = sum(
                    len(allocation) for allocation in setup.ensemble
                ) / len(setup.ensemble)
                avg_size = total / avg_n_groups
                group_size = self._project.settings["n_part_per_group"]
                return self._combined_block(
                    "Population",
                    total,
                    lambda field_id: pdata_mapped[field_id],
                    avg_size,
                    f"Shares among participants (for group size of "
                    f"{group_size}):",
                    show_percent=True,
                )
            else:
                allocation = setup.ensemble[index.column() - 1]
                p_indexes = np.concatenate(allocation)
                total = len(p_indexes)
                avg_size = total / len(allocation)
                return self._combined_block(
                    "Total size",
                    total,
                    lambda field_id, idx=p_indexes: pdata_mapped[
                        field_id
                    ].iloc[idx],
                    avg_size,
                    "Average over groups:",
                )
        elif index.row() == 1:
            # Metrics row: the ensemble-wide scores, then each allocation's
            # own diversity score.
            people_data = pdata_mapped[self._project.fields_display()]
            if index.column() == 0:
                diversity_score = setup.ensemble.calc_diversity_norm_score(
                    people_data
                )
                meeting_score = setup.ensemble.calc_meeting_norm_score()
                return (
                    f"Diversity:\n{diversity_score:.1%}\n\n"
                    f"Meetings:\n{meeting_score:.1%}"
                )
            else:
                allocation = setup.ensemble[index.column() - 1]
                diversity_score = AllocationEnsemble(
                    [allocation]
                ).calc_diversity_norm_score(people_data)
                return f"Diversity:\n{diversity_score:.1%}"

    def rowCount(self, index=...) -> int:
        """Return the fixed number of rows: statistics and metrics."""
        if self._setup is None:
            return 0
        return 2

    def columnCount(self, index=...) -> int:
        """Return the number of allocations, plus one population column."""
        if self._setup is None:
            return 0
        return len(self._setup.ensemble) + 1

    def headerData(self, section, orientation, role):
        """Return the column's allocation name or the row's caption."""
        if self._setup is None or role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return (
                "All Participants"
                if section == 0
                else self._setup.allocation_names[section - 1]
            )
        else:
            return "Statistics" if section == 0 else "Metrics"

    def flags(self, index):
        """Return flags marking cells as enabled, read-only."""
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled
