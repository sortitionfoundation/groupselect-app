from typing import Optional, Final

from PySide6 import QtCore, QtGui
from PySide6.QtWidgets import QWidget, QTableView, QAbstractItemView, QItemDelegate, QStyleOptionViewItem, QHeaderView


CELL_PADDING: Final[int] = 5


class GSResultsTableLabelDelegate(QItemDelegate):
    def paint(self,
              painter: Optional[QtGui.QPainter],
              option: QStyleOptionViewItem,
              index: QtCore.QModelIndex):
        if not index.isValid():
            return

        # Normal painting if not a participant row.
        if index.row() >= index.model().row_count_participants():
            return super(GSResultsTableLabelDelegate, self).paint(painter, option, index)

        # data is our preview object
        data = index.model().data(index, QtCore.Qt.ItemDataRole.DisplayRole)
        if data is None:
            return

        TEXT_HEIGHT = 20

        width = option.rect.width() - 2 * CELL_PADDING
        height = option.rect.height() - 2* CELL_PADDING

        # # option.rect holds the area we are painting on the widget (our table cell)
        # # scale our pixmap to fit
        # scaled = data.image.scaled(
        #     width,
        #     height,
        #     aspectRatioMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio,
        # )
        # # Position in the middle of the area.
        # x = CELL_PADDING + (width - scaled.width()) / 2
        # y = CELL_PADDING + (height - scaled.height() - TEXT_HEIGHT) / 2
        #
        # painter.drawImage(int(option.rect.x() + x), int(option.rect.y() + y), scaled)

        # Draw the title below the image, looking like a line edit
        txt_rect = QtCore.QRect(
            option.rect.x() + CELL_PADDING,
            option.rect.y() + CELL_PADDING,
            width,
            height,
        )
        painter.drawRect(
            txt_rect,
        )
        painter.drawText(
            txt_rect,
            QtCore.Qt.AlignmentFlag.AlignCenter,
            str(data),
        )


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
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
