from typing import Final

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel, QScrollArea
)
from PySide6.QtCore import Qt
from base_app.AppContext import AppContext

from GSAppFieldMode import GSAppFieldMode

_RANGE_MAX_PUBLIC: Final[float] = 0.5
_RANGE_MAX_INTERNAL: Final[int] = 100


class GSHermesSlidersPanel(QWidget):

    def __init__(self, ctx: AppContext, parent=None):
        super().__init__(parent)

        self._ctx = ctx

        self._rows: dict[int, QWidget] = {}   # field_id -> row widget (currently shown)
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
        project = self._ctx.project_manager.project
        wanted = set(project.fields_usage[GSAppFieldMode.Diversify])
        current = set(self._rows.keys())

        for field_id in current - wanted:
            self._remove_row(field_id)

        for field_id in wanted - current:
            self._add_row(field_id)

        for field_id in self._rows:
            self._labels[field_id].setText(project.data_handle.column_naming[field_id])

    # ── private ──────────────────────────────────────────────────

    def _add_row(self, field_id: int) -> None:
        project = self._ctx.project_manager.project

        # Initialise pareto_probs entry only if not already present
        # (preserves values restored from a saved project file)
        if field_id not in project.settings["pareto_probs"]:
            project.settings["pareto_probs"][field_id] = _RANGE_MAX_PUBLIC

        internal_val = self._to_internal(project.settings["pareto_probs"][field_id])

        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)

        name_label = QLabel()
        name_label.setFixedWidth(70)

        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(_RANGE_MAX_INTERNAL)
        slider.setTickInterval(5)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setPageStep(5)
        slider.setSingleStep(5)
        slider.setValue(internal_val)

        value_label = QLabel(self._fmt(internal_val))
        value_label.setFixedWidth(28)

        def on_change(raw: int, lbl=value_label, fid=field_id) -> None:
            # Snap to nearest multiple of 5
            snapped = round(raw / 5) * 5
            if slider.value() != snapped:
                slider.setValue(snapped)
                return
            self._ctx.project_manager.project.settings["pareto_probs"][fid] = self._to_public(snapped)
            lbl.setText(self._fmt(snapped))

        slider.valueChanged.connect(on_change)

        row_layout.addWidget(name_label)
        row_layout.addWidget(slider)
        row_layout.addWidget(value_label)

        self._layout.addWidget(row)
        self._rows[field_id] = row
        self._labels[field_id] = name_label

    def _remove_row(self, field_id: int) -> None:
        row = self._rows.pop(field_id)
        self._labels.pop(field_id)
        self._layout.removeWidget(row)
        row.deleteLater()

    @staticmethod
    def _to_internal(public: float) -> int:
        return round(public / _RANGE_MAX_PUBLIC * _RANGE_MAX_INTERNAL)

    @staticmethod
    def _to_public(internal: int) -> float:
        return internal / _RANGE_MAX_INTERNAL * _RANGE_MAX_PUBLIC

    @staticmethod
    def _fmt(internal: int) -> str:
        return f"{internal / _RANGE_MAX_INTERNAL * _RANGE_MAX_PUBLIC:.2f}"
