"""Reusable [0.0, 0.5]-ranged slider with a live value label.

Shared by `GSHermesSlidersPanel` (one instance per diversify field, for
HERMES's per-field `pareto_probs`) and `GSGenerateSettingsGroup` (a single
instance for DREAM's scalar `pareto_prob`).
"""

from typing import Callable, Final

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSlider, QWidget

RANGE_MAX_PUBLIC: Final[float] = 0.5
RANGE_MAX_INTERNAL: Final[int] = 100


class GSParetoSlider(QWidget):
    """A slider over [0.0, 0.5], snapping to steps of 0.05, with a label."""

    def __init__(
        self,
        initial_value: float,
        on_change: Callable[[float], None],
        parent=None,
        tooltip: str | None = None,
    ):
        """Initialise the slider at `initial_value`, calling back on change."""
        super().__init__(parent)
        self._on_change = on_change

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._slider = QSlider(Qt.Horizontal)
        if tooltip is not None:
            self.setToolTip(tooltip)
            self._slider.setToolTip(tooltip)
        self._slider.setMinimum(0)
        self._slider.setMaximum(RANGE_MAX_INTERNAL)
        self._slider.setTickInterval(5)
        self._slider.setTickPosition(QSlider.TicksBelow)
        self._slider.setPageStep(5)
        self._slider.setSingleStep(5)
        self._slider.setValue(self._to_internal(initial_value))

        self._value_label = QLabel(self._fmt(self._slider.value()))
        self._value_label.setFixedWidth(28)
        if tooltip is not None:
            self._value_label.setToolTip(tooltip)

        self._slider.valueChanged.connect(self._value_changed)

        layout.addWidget(self._slider)
        layout.addWidget(self._value_label)

    def set_value(self, value: float) -> None:
        """Move the slider to `value` without re-triggering `on_change`."""
        internal = self._to_internal(value)
        if self._slider.value() == internal:
            return
        self._slider.blockSignals(True)
        self._slider.setValue(internal)
        self._slider.blockSignals(False)
        self._value_label.setText(self._fmt(internal))

    def _value_changed(self, raw: int) -> None:
        # Snap to nearest multiple of 5.
        snapped = round(raw / 5) * 5
        if self._slider.value() != snapped:
            self._slider.setValue(snapped)
            return
        self._value_label.setText(self._fmt(snapped))
        self._on_change(self._to_public(snapped))

    @staticmethod
    def _to_internal(public: float) -> int:
        return round(public / RANGE_MAX_PUBLIC * RANGE_MAX_INTERNAL)

    @staticmethod
    def _to_public(internal: int) -> float:
        return internal / RANGE_MAX_INTERNAL * RANGE_MAX_PUBLIC

    @staticmethod
    def _fmt(internal: int) -> str:
        return f"{internal / RANGE_MAX_INTERNAL * RANGE_MAX_PUBLIC:.2f}"
