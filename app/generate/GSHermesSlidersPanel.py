"""Panel of sliders for setting per-field HERMES diversity weights."""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
)
from PySide6.QtCore import Qt
from base_app.AppContext import AppContext

from GSAppFieldMode import GSAppFieldMode
from generate.GSParetoSlider import GSParetoSlider, RANGE_MAX_PUBLIC


class GSHermesSlidersPanel(QWidget):
    """Scrollable panel showing one slider per diversify field for HERMES."""

    def __init__(self, ctx: AppContext, parent=None):
        """Initialise the panel with an empty, scrollable list of sliders."""
        super().__init__(parent)

        self._ctx = ctx

        self._rows: dict[
            int, QWidget
        ] = {}  # field_id -> row widget (currently shown)
        self._labels: dict[int, QLabel] = {}  # field_id -> slider label

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        self._container = QWidget()
        self._layout = QVBoxLayout(self._container)
        self._layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(self._container)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll)

    def update_fields(self) -> None:
        """Sync the shown sliders with the current diversify fields."""
        project = self._ctx.project_manager.project
        # `project` can be `None` here: this runs via a
        # `QTimer.singleShot(0, ...)` queued from a model signal (see
        # `GSGenerateSettingsGroup`), so the project may have been closed
        # in between that signal firing and this call actually running.
        # Treat that as "no diversify fields", clearing any sliders left
        # over from the just-closed project.
        wanted = (
            set(project.fields_usage[GSAppFieldMode.Diversify])
            if project is not None
            else set()
        )
        current = set(self._rows.keys())

        for field_id in current - wanted:
            self._remove_row(field_id)

        for field_id in wanted - current:
            self._add_row(field_id)

        for field_id in self._rows:
            self._labels[field_id].setText(
                project.data_handle.column_naming[field_id]
            )

    # ── private ──────────────────────────────────────────────────

    def _add_row(self, field_id: int) -> None:
        project = self._ctx.project_manager.project

        # Initialise pareto_probs entry only if not already present
        # (preserves values restored from a saved project file)
        if field_id not in project.settings["pareto_probs"]:
            project.settings["pareto_probs"][field_id] = RANGE_MAX_PUBLIC

        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)

        tooltip = (
            "Diversity weight for this field: higher values make the "
            "algorithm prioritise diversifying it more strongly relative "
            "to the other Diversify fields."
        )

        name_label = QLabel()
        name_label.setFixedWidth(70)
        name_label.setToolTip(tooltip)

        def on_change(value: float, fid=field_id) -> None:
            self._ctx.project_manager.project.settings["pareto_probs"][fid] = (
                value
            )

        slider = GSParetoSlider(
            project.settings["pareto_probs"][field_id],
            on_change,
            tooltip=tooltip,
        )

        row_layout.addWidget(name_label)
        row_layout.addWidget(slider)

        self._layout.addWidget(row)
        self._rows[field_id] = row
        self._labels[field_id] = name_label

    def _remove_row(self, field_id: int) -> None:
        row = self._rows.pop(field_id)
        self._labels.pop(field_id)
        self._layout.removeWidget(row)
        row.deleteLater()
