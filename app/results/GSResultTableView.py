from typing import Final, Optional

from PySide6 import QtCore, QtGui
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QItemDelegate,
    QStyleOptionViewItem,
    QTableView,
    QWidget,
)

CELL_PADDING: Final[int] = 5


class GSResultsTableLabelDelegate(QItemDelegate):
    def sizeHint(self, option, index):
        if not index.isValid():
            return super().sizeHint(option, index)

        data = index.model().data(index, QtCore.Qt.ItemDataRole.DisplayRole)

        row_count_participants = index.model().row_count_participants()
        if index.row() <= row_count_participants:
            return QtCore.QSize(option.rect.width(), 25)
        elif index.row() == row_count_participants + 2:
            data = index.model().data(
                index, QtCore.Qt.ItemDataRole.DisplayRole
            )
            if data:
                fm = QtGui.QFontMetrics(option.font)
                rect = fm.boundingRect(
                    0,
                    0,
                    option.rect.width() if option.rect.width() > 0 else 200,
                    10000,
                    QtCore.Qt.TextFlag.TextWordWrap,
                    str(data),
                )
                return QtCore.QSize(
                    option.rect.width(), rect.height() + 2 * CELL_PADDING
                )

        # Fallback rows (default painting).
        return super().sizeHint(option, index)

    def paint(
        self,
        painter: Optional[QtGui.QPainter],
        option: QStyleOptionViewItem,
        index: QtCore.QModelIndex,
    ):
        if not index.isValid():
            return

        # Draw the vertical divider line first, it will be painted over
        # by subsequent painting, but we restore it at the end.
        def draw_divider():
            if index.column() == 0:
                painter.save()
                pen = option.palette.mid().color()
                painter.setPen(pen)
                x = option.rect.right()
                painter.drawLine(x, option.rect.top(), x, option.rect.bottom())
                painter.restore()

        # Normal painting if not a participant row.
        if index.row() >= index.model().row_count_participants():
            option = QStyleOptionViewItem(option)
            option.features &= ~QStyleOptionViewItem.ViewItemFeature.WrapText
            option.displayAlignment = (
                QtCore.Qt.AlignmentFlag.AlignVCenter
                | QtCore.Qt.AlignmentFlag.AlignLeft
            )
            if index.column() != 0:
                super(GSResultsTableLabelDelegate, self).paint(
                    painter, option, index
                )
            else:
                data = index.model().data(
                    index, QtCore.Qt.ItemDataRole.DisplayRole
                )
                if data:
                    painter.drawText(
                        option.rect, option.displayAlignment, str(data)
                    )
            draw_divider()
            return

        # data is our preview object
        data = index.model().data(index, QtCore.Qt.ItemDataRole.DisplayRole)
        if data is None:
            draw_divider()
            return

        width = option.rect.width() - 2 * CELL_PADDING
        height = option.rect.height() - 2 * CELL_PADDING

        txt_rect = QtCore.QRect(
            option.rect.x() + CELL_PADDING,
            option.rect.y() + CELL_PADDING,
            width,
            height,
        )
        painter.drawRect(txt_rect)
        painter.drawText(
            txt_rect,
            QtCore.Qt.AlignmentFlag.AlignCenter,
            str(data),
        )

        draw_divider()

    def drawCheck(self, painter, option, rect, state):
        pass


class GSResultTableView(QTableView):
    def __init__(self, parent: QWidget | None = ...):
        super(GSResultTableView, self).__init__(parent=parent)
        self.verticalHeader().hide()
        self.setShowGrid(False)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setItemDelegate(GSResultsTableLabelDelegate())
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDefaultDropAction(QtCore.Qt.DropAction.MoveAction)
        self.setDragDropOverwriteMode(False)
        self.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
