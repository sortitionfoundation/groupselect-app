"""Group box for assigning field usage modes via drag-and-drop lists."""

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPalette
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QListView,
)

from GSAppFieldMode import (
    GSAppFieldMode,
    FIELD_MODE_LABELS,
    FIELD_MODE_TOOLTIPS,
)
from models.GSFieldUsageListModel import GSFieldUsageListModel

if TYPE_CHECKING:
    from base_app.AppContext import AppContext


class _FieldListView(QListView):
    """A QListView that shows a hint in place of an empty field list."""

    _EMPTY_TEXT = "(empty — drop field to add)"

    def paintEvent(self, event):
        """Paint the normal list, or the empty-list hint if it has no rows."""
        super(_FieldListView, self).paintEvent(event)
        if self.model() is None or self.model().rowCount() > 0:
            return

        # Some platform themes leave QPalette::PlaceholderText
        # indistinguishable from the background, so derive a
        # guaranteed-visible mid-tone by blending the list's actual
        # text and background colours.
        text_color = self.palette().color(QPalette.ColorRole.Text)
        base_color = self.palette().color(QPalette.ColorRole.Base)
        hint_color = QColor(
            (text_color.red() + base_color.red()) // 2,
            (text_color.green() + base_color.green()) // 2,
            (text_color.blue() + base_color.blue()) // 2,
        )

        painter = QPainter(self.viewport())
        painter.setPen(hint_color)
        painter.drawText(
            self.viewport().rect(),
            Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
            self._EMPTY_TEXT,
        )


class GSGenerateFieldsGroup(QGroupBox):
    """Group box with a drag-and-drop field list per usage mode."""

    _ctx: "AppContext"

    def __init__(self, ctx: "AppContext"):
        """Initialise the group box and build the field lists."""
        super(GSGenerateFieldsGroup, self).__init__("Field settings")
        self._ctx = ctx

        self._create_ui()

    def _create_ui(self):
        self.setToolTip(
            "Drag and drop participant-data columns between these lists to "
            "choose how each is used by the allocation algorithm."
        )
        horizontal_layout = QHBoxLayout()
        for usage_mode in GSAppFieldMode:
            horizontal_layout.addWidget(
                self._create_list(
                    FIELD_MODE_LABELS[usage_mode],
                    FIELD_MODE_TOOLTIPS[usage_mode],
                    self._ctx.model_manager[f"fu{usage_mode.name.lower()}"],
                )
            )
        self.setLayout(horizontal_layout)

    def _create_list(
        self, name: str, tooltip: str, model: GSFieldUsageListModel
    ):
        list = _FieldListView()
        list.setModel(model)
        list.setDragEnabled(True)
        list.setAcceptDrops(True)
        list.setDropIndicatorShown(True)
        list.setToolTip(tooltip)
        # list.setDragDropMode(QAbstractItemView.DragDrop)
        # list.setDefaultDropAction(Qt.MoveAction)
        # list.setMovement(QListView.Snap)

        label = QLabel(name)
        label.setToolTip(tooltip)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(list)
        widget = QWidget()
        widget.setLayout(layout)

        return widget
