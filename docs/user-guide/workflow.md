# Workflow

This page walks through the full process of generating group allocations
from imported participant data.

## Step 1 — Assign field roles (Participants tab)

After importing data, open the **Participants → Fields** sub-tab. You will
see five lists of column names:

| Role | Description |
|------|-------------|
| **Ignore** | Not used by the algorithm (default for all columns) |
| **Diversify** | Distribute participants proportionally; each group mirrors the population distribution of this field |
| **Cluster** | Keep participants sharing a specific value in the same group(s) |
| **Display** | Not used for allocation but shown in the results table |
| **Label** | Used as the participant identifier in the results (e.g. name column) |

**Drag** column names between the lists to assign roles.

### Term substitutions

In the **Fields** sub-tab, select a column name from the list on the left.
A table on the right shows each unique value in that column. You can type
an alternative label (e.g. map `"M"` → `"Male"`) to make the results more
readable. These substitutions are applied before the algorithm runs.

## Step 2 — Configure the algorithm (Generate tab)

### Field Settings panel

Shows the same five field-role lists as the Participants tab. You can
continue reassigning columns here before running.

### Allocation Settings panel

| Setting | Description |
|---------|-------------|
| **Group size** | Target number of participants per group |
| **Algorithm** | HERMES (recommended), DREAM, or Legacy |
| **Diversity weights** | Per-field sliders (HERMES only, see below) |
| **Number of groups** | Computed automatically from group size and participant count |
| **Number of allocations** | Number of session rounds to generate |
| **Advanced Settings → Modify** | Set `n_attempts` (quality vs speed) and `seed` (reproducibility) |

### Manual allocations

Use the **Manual Allocations** panel to force specific participants into
specific groups. Click **Add**, then select a participant and a group
number. Click **Delete** to remove a manual constraint.

### HERMES diversity weights

When HERMES is selected, a slider appears for each `Diversify` field. The
slider ranges from `0.0` (left) to `0.5` (right):

- **`0.5` (full weight)**: strict diversity enforcement — equivalent to the
  DREAM algorithm. The algorithm will prioritise keeping this field's
  distribution balanced across groups.
- **`0.0` (no weight)**: diversity for this field is not enforced; the
  algorithm is free to arrange participants however best maximises unique
  meetings.

Intermediate values provide a smooth trade-off.

## Step 3 — Generate

Click **Generate Groups!**. A progress bar shows the algorithm running.
When complete, a summary dialog shows:

- **Diversity score**: sum of per-field L1 deviations from the ideal
  distribution (lower is better).
- **Meeting score**: normalised fraction of unique pair meetings achieved
  (higher is better, 100% = theoretical maximum).

The new allocations are appended to the results list.

## Step 4 — Browse and export results (Results tab)

The **Results** tab shows a list of all generated allocations on the left
and a detailed table for the selected allocation on the right.

The table shows each group's members, along with the demographic
distribution for the Display and Diversify fields.

You can manually reassign participants between groups by editing the table
directly.

## Saving your project

Use **File → Save** (`Ctrl+S`) to save all settings, imported data, term
substitutions, and results to a `.gspr` project file. Reopen it later with
**File → Open**.
