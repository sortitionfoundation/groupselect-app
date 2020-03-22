# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class TAHelpDialog(QtWidgets.QDialog):
    def __init__(self, about_html, parent = None):
        super(TAHelpDialog, self).__init__(parent)
        self.setupUi(about_html)

    def setupUi(self, about_html):
        self.setFixedSize(400, 300)
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.label = QtWidgets.QLabel(self)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setWordWrap(True)
        layout.addWidget(self.label)

        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("About Dialog", "About this Software"))
        self.label.setText(about_html)

    @staticmethod
    def show(about_html, parent = None):
        dialog = TAHelpDialog(about_html, parent)
        dialog.exec_()

