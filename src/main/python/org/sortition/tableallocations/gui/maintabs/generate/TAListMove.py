import PyQt5.QtWidgets as QtWidgets, PyQt5.QtCore as QtCore
from PyQt5.QtCore import Qt

class TAListMove(QtWidgets.QListWidget):
    trigger = QtCore.pyqtSignal()

    def __init__(self):
        super(TAListMove, self).__init__()
        self.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setDragEnabled(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.setDropIndicatorShown(True)
        self.setMovement(QtWidgets.QListView.Snap)
        self.setProperty("isWrapping", False)
        self.setWordWrap(False)
        self.setSortingEnabled(False)
        self.setAcceptDrops(True)
        self.installEventFilter(self)

    def eventFilter(self, sender, event):
        if (event.type() == QtCore.QEvent.ChildRemoved):
            self.trigger.emit()
        return False
