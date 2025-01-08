from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QTableView

from org.sortition.groupselect.gui.mainmenu.import_dialogs.TAColmapDataModel import TAColmapDataModel


class TAColmapDialog(QtWidgets.QDialog):
    def __init__(self, parent, keys: list, old_keys: list, colmap: list):
        super(TAColmapDialog, self).__init__(parent)

        self.model = TAColmapDataModel(keys, old_keys, colmap)

        self.__setupUi()

        self.ok = False


    def __setupUi(self):
        # table
        self.__table = QTableView()
        self.__table.setModel(self.model)

        # buttons
        self.btn_ok = QPushButton('Ok')
        self.btn_ok.clicked.connect(self.__buttonPress)
        self.btn_cancel = QPushButton('Cancel')
        self.btn_cancel.clicked.connect(self.__buttonPress)
        self.btn_cancel.move(80, 0)

        buttons = QHBoxLayout()
        buttons.addWidget(self.btn_ok)
        buttons.addWidget(self.btn_cancel)
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons)

        vbox = QVBoxLayout()
        vbox.addSpacing(15)
        vbox.addWidget(QLabel('Please select which existing columns the imported columns should be mapped to.', self))
        vbox.addWidget(self.__table)
        vbox.addWidget(buttons_widget)
        self.setLayout(vbox)


    def __buttonPress(self):
        self.ok = (self.sender() == self.btn_ok)
        self.close()


    @classmethod
    def get_input(cls, parent, keys: list, old_keys: list, colmap: list, skip: bool = False):
        if skip and colmap and len(keys) == len(colmap):
            return True, colmap

        dialog = cls(parent, keys, old_keys, colmap)
        dialog.exec_()
        if dialog.ok:
            return dialog.ok, dialog.model.getColmap()
        else:
            return dialog.ok, colmap
