# Getting Started

## Installation

Download the pre-built installer for your operating system from the
[releases page](https://github.com/sortitionfoundation/groupselect-app/releases)
and run it. No Python installation is required.

## Preparing your data file

The app accepts Excel (`.xlsx`, `.xls`) or CSV (`.csv`, `.tsv`, `.ssv`)
files. Your file should have:

- **One row per participant.**
- **One column per attribute** (name, gender, age bracket, dietary needs,
  accessibility requirements, etc.).
- A **header row** with column names.

Not every column needs to be used by the algorithm — you can import as
many columns as you like and decide per column whether it influences the
grouping.

**Example:**

| Name | Gender | Age | Dietary | Audio consent |
|------|--------|-----|---------|---------------|
| Alice | Female | 30–44 | Vegan | Yes |
| Bob | Male | 45–59 | None | No |
| … | … | … | … | … |

## Creating a new project

1. Start the app.
2. Go to **File → New** (or use the keyboard shortcut shown in the menu).
3. Choose a folder where the project file (`.gspr`) will be saved.

## Importing participant data

1. Go to **Data → Import file** (`Ctrl+I`).
2. Select your spreadsheet.
3. A preview dialog opens. Choose:
   - Which **row** the data starts on (to skip any secondary headers).
   - Which **columns** to import.
4. Click **OK**.

Your data now appears in the **Participants → Data** sub-tab.

To reload the data from the same file after changes (e.g. if you add
participants), use **Data → Update import** (`Shift+F5`).

## What's next

Continue to [Workflow](workflow.md) to learn how to configure fields,
set algorithm parameters, and generate groups.
