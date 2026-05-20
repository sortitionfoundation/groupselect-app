# Architecture

## Overview

The app is built on the **`base-app`** framework (a Sortition Foundation
internal package), which provides the application context, project
management, and Qt MVC scaffolding. The GroupSelect app extends these
base classes with domain-specific logic.

```
AppContext (base-app)
├── project_manager  →  GSProject
├── model_manager    →  GSModelManager
└── main_window      →  GSMainWindow
                            └── GSMainTabs
                                ├── GSParticipantsTab
                                ├── GSGenerateTab
                                └── GSResultsTab
```

`AppContext` is the central dependency-injection container. Every widget
receives a reference to it and accesses project state via
`ctx.project_manager.project` and Qt models via `ctx.model_manager["key"]`.

## Key classes

### GSProject (`app/GSProject.py`)

Holds all mutable project state. Persisted to/from `.gspr` project files.

```python
class GSProject(AbstractProject):
    data_handle: GSDataImportHandle     # raw file + column naming
    terms: dict                         # value-label substitutions
    fields_usage: dict[GSAppFieldMode, list[int]]  # column assignment
    manuals: dict[int, int]             # {participant_idx: group_idx}
    settings: dict                      # algorithm parameters
    results: AllocationEnsemble         # computed allocations
```

The `pdata` property returns the raw imported DataFrame; `pdata_mapped`
applies `terms` substitutions and caches the result. Call
`clear_cache_mapped()` after editing terms.

### GSAppFieldMode (`app/GSAppFieldMode.py`)

Extends the lib's `FieldMode` concept with two app-only roles:

- `Display`: shown in results but not used during allocation.
- `Label`: used as the participant identifier in result views.

`map_field_modes(mode)` converts to the lib's `FieldMode` for passing to
`allocate_pandas`.

### GSModelManager (`app/GSModelManager.py`)

Manages Qt MVC models. Accessed via `ctx.model_manager["key"]`.

| Key | Model | Purpose |
|-----|-------|---------|
| `"pdata"` | `GSParticipantsDataModel` | Participants data table |
| `"pfields"` | `GSParticipantsFieldsModel` | Column list for term editing |
| `"pterms"` | `GSParticipantsTermsModel` | Value-label substitution table |
| `"almanuals"` | `GSManualsListModel` | Manual allocation list |
| `"alsettings"` | `GSAllocationSettingsModel` | Algorithm settings form |
| `"results_list"` | `GSResultsListModel` | List of allocations |
| `"results_table"` | `GSResultsTableModel` | Selected allocation table |
| `"fu{mode}"` | `GSFieldUsageListModel` | Drag-drop field lists per mode |

After modifying participant data call `model_manager.updated_participants()`.
After generating allocations call `model_manager.updated_results()`.

## Data flow

### Import

```
File on disk
  → GSDataImportHandle (stores file path + column selection)
  → import_data() reads with pandas
  → GSProject.data_handle
  → model_manager.updated_participants()
```

### Allocation

```
GSGenerateSettingsGroup._button_clicked (btn_run)
  → read project.settings, fields_usage, pdata_mapped
  → allocate_pandas(pdata_mapped, fields, n_part_per_group, ...)
  → AllocatorResult.ensemble
  → project.results.extend(ensemble)
  → model_manager.updated_results()
```

### Settings

`GSAllocationSettingsModel` is connected to the settings form via a
`QDataWidgetMapper`. Changes in the UI widgets (group size, algorithm,
number of allocations) are reflected in `project.settings` automatically.

## HERMES sliders (`app/generate/GSHermesSlidersPanel.py`)

Creates one row per `Diversify` field. Slider range: 0 to 0.5 (public),
stored internally as 0–100 integers, snapping to multiples of 5. Values
are written to `project.settings["pareto_probs"][field_id]`. The panel
responds to changes in the `fudiversify` field list model and adds/removes
rows dynamically.

## Build system

Uses [Nuitka](https://nuitka.net/) to compile to a standalone executable.
GitHub Actions (`.github/workflows/build.yml`) handles building for all
platforms. Python 3.11 is pinned (`.python-version`).
