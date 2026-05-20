# GroupSelect App

The GroupSelect App is a standalone desktop application for Citizens'
Assembly organisers. It allows you to import participant data, configure
demographic field roles, and generate optimised group allocations — without
writing any code.

## What it does

Given a spreadsheet of participants and their demographic attributes, the
app partitions them into discussion groups for each session of the assembly.
It optimises two objectives simultaneously:

- **Diversity**: each group mirrors the full-population demographic
  distribution across selected fields.
- **Uniqueness**: across multiple sessions, participants meet as many
  different fellow participants as possible.

## Download

Pre-built executables for Windows, macOS, and Linux are available from the
[releases page](https://github.com/sortitionfoundation/groupselect-app/releases).

## Supported data formats

- Excel spreadsheets (`.xlsx`, `.xls`)
- Delimiter-separated plain-text files (`.csv`, `.tsv`, `.ssv`)

## Quick overview

1. **Import** your participant spreadsheet via *Data → Import file*.
2. **Assign fields** to roles (Diversify / Cluster / Display / Ignore) by
   dragging column names between the lists in the Participants tab.
3. **Configure** group size, number of sessions, algorithm, and HERMES
   diversity weights in the Generate tab.
4. **Generate** by clicking "Generate Groups!".
5. **Browse** and export results in the Results tab.

See the [User Guide](user-guide/getting-started.md) for step-by-step
instructions.

## Algorithms

The app supports three algorithms from the `groupselect` library:

| Algorithm | Description |
|-----------|-------------|
| HERMES | Per-field diversity weights (recommended) |
| DREAM | Equal diversity weighting |
| Legacy | Simple greedy restart |

The default is **HERMES**, which exposes per-field sliders for fine-grained
control over the diversity/meetings trade-off.

## For developers

See the [Architecture](developer/architecture.md) page for an overview of
the code structure.
