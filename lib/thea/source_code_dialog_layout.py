# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'source_code_dialog_layout.ui'
#
# Created: Mon Sep 23 16:00:33 2013
#      by: pyside-uic 0.2.13 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(632, 434)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.code_browser = QtGui.QTextBrowser(Dialog)
        self.code_browser.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.code_browser.setObjectName("code_browser")
        self.gridLayout.addWidget(self.code_browser, 0, 1, 1, 2)
        self.ok_button = QtGui.QPushButton(Dialog)
        self.ok_button.setObjectName("ok_button")
        self.gridLayout.addWidget(self.ok_button, 1, 2, 1, 1)
        self.save_button = QtGui.QPushButton(Dialog)
        self.save_button.setObjectName("save_button")
        self.gridLayout.addWidget(self.save_button, 1, 1, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.ok_button, QtCore.SIGNAL("clicked()"), Dialog.close)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.ok_button.setText(QtGui.QApplication.translate("Dialog", "Ok", None, QtGui.QApplication.UnicodeUTF8))
        self.save_button.setText(QtGui.QApplication.translate("Dialog", "Save", None, QtGui.QApplication.UnicodeUTF8))

