# GroupSelect App — LLM context

## Purpose

The GroupSelect App is a standalone PySide6 desktop application for CA
practitioners. It provides a GUI wrapper around the `groupselect` library,
letting users import participant data, configure field roles, and generate
optimised group allocations without writing code.

Target audience: Citizens' Assembly organisers, not developers.

## Repository layout

```
app/
├── main.py                        # Entry point
├── GSAppFieldMode.py              # App-level field mode enum + mapping
├── GSProject.py                   # Project data model
├── GSModelManager.py              # Qt model registry
├── GSMainWindow.py                # Main window + menu + file import
├── GSMainTabs.py                  # Top-level tab widget
├── participants/                  # Tab 0: view and configure participants
│   ├── GSParticipantsTab.py
│   ├── GSParticipantsDataSubtab.py
│   └── GSParticipantsFieldsSubtab.py
├── generate/                      # Tab 1: configure and run allocation
│   ├── GSGenerateTab.py
│   ├── GSGenerateFieldsGroup.py   # Drag-drop field assignment lists
│   ├── GSGenerateSettingsGroup.py # Algorithm settings + run button
│   ├── GSHermesSlidersPanel.py    # Per-field pareto_prob sliders
│   ├── GSAdvancedSettingsDialog.py
│   └── GSManualDialog.py
├── results/                       # Tab 2: browse + export results
│   ├── GSResultsTab.py
│   └── GSResultTableView.py
├── importing/                     # File import machinery
│   ├── GSDataImportHandle.py
│   ├── GSPreviewDialog.py
│   ├── GSPreviewTableModel.py
│   └── GSPreviewTableView.py
└── models/                        # Qt MVC models
    ├── GSAllocationSettingsModel.py
    ├── GSFieldUsageListModel.py
    ├── GSManualsListModel.py
    ├── GSParticipantsDataModel.py
    ├── GSParticipantsFieldsModel.py
    ├── GSParticipantsTermsModel.py
    ├── GSResultsListModel.py
    └── GSResultsTableModel.py
```

## External dependencies

These packages are sourced from private Sortition Foundation GitHub repos
and provide the application framework. They are **not** in this repo.

- **`base-app`** (tag v0.1.0): `AppContext`, `AbstractMainWindow`,
  `AbstractProject`, `AbstractModelManager`, `AbstractProjectModel`
- **`datahandling`** (tag v0.1.0): `DataHandle` (reads CSV/XLS files)

## Architecture overview

```
AppContext (from base-app)
├── .project_manager  → holds GSProject
├── .model_manager    → GSModelManager
└── .main_window      → GSMainWindow
                           └── GSMainTabs
                               ├── GSParticipantsTab
                               ├── GSGenerateTab
                               └── GSResultsTab
```

`AppContext` is the central dependency-injection object passed to every
widget. Access project state via `ctx.project_manager.project`; access Qt
models via `ctx.model_manager["model_key"]`.

## GSProject — project state

```python
class GSProject(AbstractProject):
    data_handle: GSDataImportHandle  # raw file + column naming
    terms: dict                      # value substitutions per column
    fields_usage: dict[GSAppFieldMode, list[int]]  # column → usage
    manuals: dict[int, int]          # forced {participant_idx: group_idx}
    settings: dict                   # algorithm settings (see below)
    results: AllocationEnsemble      # computed allocations
```

`settings` keys: `n_part_per_group`, `n_allocations`, `n_attempts`, `seed`,
`algorithm` (str name), `pareto_probs` (dict[int, float] for HERMES).

`pdata` property: the raw imported DataFrame (from `data_handle`).
`pdata_mapped` property: pdata with `terms` substitutions applied (cached).

## GSAppFieldMode

Extends the lib's `FieldMode` concept with two app-only modes:

| Mode | Used in lib? | Description |
|------|-------------|-------------|
| `Ignore` | Yes | Not used in allocation |
| `Diversify` | Yes | Proportional distribution |
| `Cluster` | Yes | Keep together in subset of groups |
| `Display` | No (mapped to Ignore) | Show in results but don't allocate |
| `Label` | No (mapped to Ignore) | Use as participant identifier |

`map_field_modes(mode)` converts to lib's `FieldMode`.

## GSModelManager — Qt model registry

Models are accessed by string key via `ctx.model_manager["key"]`.

| Key | Model class | What it drives |
|-----|-------------|----------------|
| `"pdata"` | GSParticipantsDataModel | Participants data table view |
| `"pfields"` | GSParticipantsFieldsModel | Field list in Fields subtab |
| `"pterms"` | GSParticipantsTermsModel | Term substitution table |
| `"almanuals"` | GSManualsListModel | Manual allocations list |
| `"alsettings"` | GSAllocationSettingsModel | Settings form via QDataWidgetMapper |
| `"results_list"` | GSResultsListModel | List of computed allocations |
| `"results_table"` | GSResultsTableModel | Allocation table display |
| `"fu{mode}"` | GSFieldUsageListModel | Drag-drop field usage lists |

After changing project data call `model_manager.updated_participants()`;
after generating call `model_manager.updated_results()`.

## Generate workflow

`GSGenerateSettingsGroup._button_clicked` (sender == `_btn_run`):

1. Reads settings from `project.settings`.
2. Converts `fields_usage` → `fields: dict[str, FieldMode]` via
   `map_field_modes`.
3. Calls `allocate_pandas(pdata_mapped, fields, n_allocations * [n_part_per_group], ...)`.
   Note: each allocation round is an entry in the `n_part_per_group` list.
4. On success: appends ensemble to `project.results`; shows scores in dialog.

## HERMES sliders

`GSHermesSlidersPanel` renders one slider per `Diversify` field. Slider
range: 0 (internal 0) to 0.5 (internal 100), snapping to multiples of 5
(internal), i.e. 0.025 steps. Values stored in
`project.settings["pareto_probs"][field_id]`.

## Build

Nuitka-based standalone executable. See `.github/workflows/build.yml`.
Python 3.11 is pinned (strict requirement from PySide6 version used).
Project files saved as `.gspr`.
