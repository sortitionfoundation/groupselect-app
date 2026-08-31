"""Builds the tables exported by "Export as.../Export", and writes them out.

Mirrors, deliberately kept independent of, the content shown by
`GSResultsTableModel` (one allocation) and `GSSetupSummaryTableModel` (one
setup's summary) -- reusing those models directly wasn't an option since
their `update_current()` mutates `project.selected_setup`/
`selected_allocation`, which would silently change what the Results tab is
showing on screen mid-export.
"""

import numpy as np
import pandas as pd

from groupselect import AllocationEnsemble

from GSAppFieldMode import GSAppFieldMode
from GSExportSettings import GSExportSelection, GSExportSettings
from GSProject import GSProject
from GSSetup import GSSetup


# Characters not allowed in an Excel sheet name, plus its length limit.
_INVALID_SHEET_CHARS = set(":\\/?*[]")
_MAX_SHEET_NAME_LEN = 31


def _participant_label(project: GSProject, pdata_mapped, p_index) -> str:
    label_fields = project.fields_usage[GSAppFieldMode.Label]
    if label_fields:
        return (
            " ".join(pdata_mapped.loc[p_index, label_fields]) + f" ({p_index})"
        )
    return str(p_index)


def build_raw_dataframe(project: GSProject) -> pd.DataFrame:
    """Return the raw imported participants' data, with display columns."""
    return project.pdata.rename(columns=project.data_handle.column_naming)


def build_mapped_dataframe(project: GSProject) -> pd.DataFrame:
    """Return the term-mapped participants' data, with display column names."""
    return project.pdata_mapped.rename(
        columns=project.data_handle.column_naming
    )


def build_terminology_dataframe(project: GSProject) -> pd.DataFrame:
    """Return one row per (column, raw term found, term used) triple."""
    rows = []
    for col_id, col_name in project.data_handle.column_naming.items():
        raw_values = sorted(
            v for v in project.pdata[col_id].unique() if v is not None
        )
        used_by_found = dict(project.terms.get(col_id, []))
        for raw_value in raw_values:
            rows.append(
                {
                    "Column": col_name,
                    "Term found": raw_value,
                    "Term used": used_by_found.get(raw_value, raw_value),
                }
            )
    return pd.DataFrame(rows, columns=["Column", "Term found", "Term used"])


def _field_stats_lines(
    project: GSProject,
    pdata_mapped: pd.DataFrame,
    get_field_values,
    avg_size: float,
    total: int,
    show_percent: bool = False,
) -> list[str]:
    r"""Return one "<field>:\n<n> <term>\n..." block per displayed field.

    `get_field_values(field_id)` returns the (mapped) values of that field
    for the relevant subset of participants, as a pandas Series.
    """
    per_term_factor = avg_size / total if total else 0.0
    lines = []
    for field_id in project.fields_display():
        field_name = project.data_handle.column_naming[field_id]
        value_counts = get_field_values(field_id).value_counts()
        if show_percent:
            terms = "\n".join(
                f"{term_count / total * 100:.1f}% "
                f"({term_count * per_term_factor:.1f}) {term_name}"
                for (term_name, term_count) in value_counts.items()
            )
        else:
            terms = "\n".join(
                f"{term_count * per_term_factor:.1f} {term_name}"
                for (term_name, term_count) in value_counts.items()
            )
        lines.append(f"{field_name}:\n{terms}")
    return lines


def build_allocation_dataframe(
    project: GSProject, setup: GSSetup, allocation_index: int
) -> pd.DataFrame:
    """Return one allocation's groups as columns, like the results table."""
    allocation = setup.ensemble[allocation_index]
    pdata_mapped = project.pdata_mapped

    n_participant_rows = max(len(group) for group in allocation)
    group_columns = [f"Group {i + 1}" for i in range(len(allocation))]
    columns = ["Overall"] + group_columns
    n_rows = n_participant_rows + 2  # + group-stats row + diversity row
    data = {col: [None] * n_rows for col in columns}

    for g_idx, group in enumerate(allocation):
        for p_row, p_id in enumerate(group):
            p_index = pdata_mapped.index[p_id]
            data[group_columns[g_idx]][p_row] = _participant_label(
                project, pdata_mapped, p_index
            )

    # "Total size" + per-field breakdown, for the allocation as a whole.
    total = sum(len(group) for group in allocation)
    avg_size = total / len(allocation)
    p_indexes_all = np.concatenate(allocation)
    lines = [f"Total size:\n{total}"] + _field_stats_lines(
        project,
        pdata_mapped,
        lambda fid: pdata_mapped[fid].iloc[p_indexes_all],
        avg_size,
        total,
    )
    data["Overall"][n_participant_rows] = "\n\n".join(lines)

    # "Group size" + per-field breakdown, for each group individually.
    for g_idx, group in enumerate(allocation):
        lines = [f"Group size:\n{len(group)}"] + _field_stats_lines(
            project,
            pdata_mapped,
            lambda fid, idx=group: pdata_mapped[fid].iloc[idx],
            len(group),
            len(group),
        )
        data[group_columns[g_idx]][n_participant_rows] = "\n\n".join(lines)

    # Diversity score of this one allocation (no meeting score -- that's an
    # ensemble-wide metric, not meaningful for a single allocation).
    people_data = pdata_mapped[project.fields_display()]
    diversity_score = AllocationEnsemble(
        [allocation]
    ).calc_diversity_norm_score(people_data)
    data["Overall"][n_participant_rows + 1] = (
        f"Diversity:\n{diversity_score:.1%}"
    )

    return pd.DataFrame(data)


def build_setup_summary_dataframe(
    project: GSProject, setup: GSSetup
) -> pd.DataFrame:
    """Return the setup summary: the population, then per allocation."""
    pdata_mapped = project.pdata_mapped
    total = len(pdata_mapped)
    avg_n_groups = sum(len(a) for a in setup.ensemble) / len(setup.ensemble)
    avg_size = total / avg_n_groups
    group_size = project.settings["n_part_per_group"]

    pop_lines = [
        f"Population:\n{total}",
        f"Shares among participants (for group size of {group_size}):",
    ] + _field_stats_lines(
        project,
        pdata_mapped,
        lambda fid: pdata_mapped[fid],
        avg_size,
        total,
        show_percent=True,
    )

    people_data = pdata_mapped[project.fields_display()]
    pop_diversity = setup.ensemble.calc_diversity_norm_score(people_data)
    pop_meeting = setup.ensemble.calc_meeting_norm_score()

    stats_row = {"All Participants": "\n\n".join(pop_lines)}
    metrics_row = {
        "All Participants": (
            f"Diversity:\n{pop_diversity:.1%}\n\nMeetings:\n{pop_meeting:.1%}"
        )
    }

    for name, allocation in zip(setup.allocation_names, setup.ensemble):
        p_indexes = np.concatenate(allocation)
        a_total = len(p_indexes)
        a_avg_size = a_total / len(allocation)
        lines = [
            f"Total size:\n{a_total}",
            "Average over groups:",
        ] + _field_stats_lines(
            project,
            pdata_mapped,
            lambda fid, idx=p_indexes: pdata_mapped[fid].iloc[idx],
            a_avg_size,
            a_total,
        )
        stats_row[name] = "\n\n".join(lines)
        a_diversity = AllocationEnsemble(
            [allocation]
        ).calc_diversity_norm_score(people_data)
        metrics_row[name] = f"Diversity:\n{a_diversity:.1%}"

    columns = ["All Participants"] + list(setup.allocation_names)
    return pd.DataFrame(
        [stats_row, metrics_row], index=["Statistics", "Metrics"]
    )[columns]


def _sanitize_sheet_name(name: str) -> str:
    cleaned = "".join(c for c in name if c not in _INVALID_SHEET_CHARS)
    return cleaned.strip() or "Sheet"


def _unique_sheet_name(name: str, used: set[str]) -> str:
    base = _sanitize_sheet_name(name)[:_MAX_SHEET_NAME_LEN]
    candidate = base
    n = 2
    while candidate in used:
        suffix = f" ({n})"
        candidate = base[: _MAX_SHEET_NAME_LEN - len(suffix)] + suffix
        n += 1
    used.add(candidate)
    return candidate


def resolve_components(
    project: GSProject, selection: GSExportSelection
) -> list[tuple[str, pd.DataFrame]]:
    """Expand a selection into the concrete (name, dataframe) pairs to write.

    Setups/allocations that no longer exist (e.g. deleted since the
    selection was made) are silently skipped.
    """
    components = []

    if selection.raw_data and project.pdata is not None:
        components.append(("Raw Data", build_raw_dataframe(project)))
    if selection.mapped_data and project.pdata_mapped is not None:
        components.append(("Mapped Data", build_mapped_dataframe(project)))
    if selection.terminology and project.pdata is not None:
        components.append(
            ("Terminology", build_terminology_dataframe(project))
        )

    for setup in project.setups:
        scope = (
            "all"
            if selection.all_results
            else selection.setups.get(setup.setup_id)
        )
        if scope is None:
            continue

        if scope in ("all", "summary_only") and setup.ensemble:
            components.append(
                (
                    f"{setup.name} - Summary",
                    build_setup_summary_dataframe(project, setup),
                )
            )

        if scope == "all":
            wanted_allocation_ids = set(setup.allocation_ids)
        elif isinstance(scope, set):
            wanted_allocation_ids = scope
        else:
            wanted_allocation_ids = set()

        for a_idx, a_id in enumerate(setup.allocation_ids):
            if a_id in wanted_allocation_ids:
                components.append(
                    (
                        f"{setup.name} - {setup.allocation_names[a_idx]}",
                        build_allocation_dataframe(project, setup, a_idx),
                    )
                )

    return components


def export_to_file(project: GSProject, settings: GSExportSettings):
    """Write the selected components to `settings.file_path`."""
    components = resolve_components(project, settings.selection)
    if not components:
        raise Exception(
            "Nothing to export -- the selected item(s) may have been "
            'renamed or deleted. Please use "Export as..." again to '
            "choose what to export."
        )

    if settings.file_format == "csv":
        _, dataframe = components[0]
        dataframe.to_csv(
            settings.file_path,
            sep=settings.csv_sep,
            quotechar=settings.csv_quote,
            index=False,
        )
    else:
        used_names: set[str] = set()
        with pd.ExcelWriter(settings.file_path, engine="openpyxl") as writer:
            for raw_name, dataframe in components:
                sheet_name = _unique_sheet_name(raw_name, used_names)
                dataframe.to_excel(writer, sheet_name=sheet_name, index=False)
