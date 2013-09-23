# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'colorbar_dialog_layout.ui'
#
# Created: Mon Sep 23 16:00:34 2013
#      by: pyside-uic 0.2.13 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_ColorbarDialog(object):
    def setupUi(self, ColorbarDialog):
        ColorbarDialog.setObjectName("ColorbarDialog")
        ColorbarDialog.resize(418, 199)
        self.gridLayout = QtGui.QGridLayout(ColorbarDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.autoselect_range = QtGui.QCheckBox(ColorbarDialog)
        self.autoselect_range.setChecked(True)
        self.autoselect_range.setObjectName("autoselect_range")
        self.gridLayout.addWidget(self.autoselect_range, 7, 1, 1, 1)
        self.fixed_colorbar = QtGui.QCheckBox(ColorbarDialog)
        self.fixed_colorbar.setObjectName("fixed_colorbar")
        self.gridLayout.addWidget(self.fixed_colorbar, 7, 2, 1, 1)
        self.manual_range = QtGui.QCheckBox(ColorbarDialog)
        self.manual_range.setObjectName("manual_range")
        self.gridLayout.addWidget(self.manual_range, 7, 3, 1, 1)
        self.ok_button = QtGui.QPushButton(ColorbarDialog)
        self.ok_button.setObjectName("ok_button")
        self.gridLayout.addWidget(self.ok_button, 8, 2, 1, 1)
        self.max_contour = QtGui.QDoubleSpinBox(ColorbarDialog)
        self.max_contour.setEnabled(False)
        self.max_contour.setMinimum(-999999999.0)
        self.max_contour.setMaximum(999999999.0)
        self.max_contour.setObjectName("max_contour")
        self.gridLayout.addWidget(self.max_contour, 6, 2, 1, 2)
        self.label = QtGui.QLabel(ColorbarDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 6, 1, 1, 1)
        self.label_2 = QtGui.QLabel(ColorbarDialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 5, 1, 1, 1)
        self.min_contour = QtGui.QDoubleSpinBox(ColorbarDialog)
        self.min_contour.setEnabled(False)
        self.min_contour.setMinimum(-999999999.0)
        self.min_contour.setMaximum(999999999.0)
        self.min_contour.setObjectName("min_contour")
        self.gridLayout.addWidget(self.min_contour, 5, 2, 1, 2)

        self.retranslateUi(ColorbarDialog)
        QtCore.QObject.connect(self.manual_range, QtCore.SIGNAL("toggled(bool)"), self.max_contour.setEnabled)
        QtCore.QObject.connect(self.manual_range, QtCore.SIGNAL("toggled(bool)"), self.min_contour.setEnabled)
        QtCore.QObject.connect(self.ok_button, QtCore.SIGNAL("clicked()"), ColorbarDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(ColorbarDialog)

    def retranslateUi(self, ColorbarDialog):
        ColorbarDialog.setWindowTitle(QtGui.QApplication.translate("ColorbarDialog", "Colorbar Range", None, QtGui.QApplication.UnicodeUTF8))
        self.autoselect_range.setToolTip(QtGui.QApplication.translate("ColorbarDialog", "Select the range over which the colorbar is set", None, QtGui.QApplication.UnicodeUTF8))
        self.autoselect_range.setText(QtGui.QApplication.translate("ColorbarDialog", "Automatic", None, QtGui.QApplication.UnicodeUTF8))
        self.autoselect_range.setShortcut(QtGui.QApplication.translate("ColorbarDialog", "A", None, QtGui.QApplication.UnicodeUTF8))
        self.fixed_colorbar.setText(QtGui.QApplication.translate("ColorbarDialog", "Fix Across all Slices", None, QtGui.QApplication.UnicodeUTF8))
        self.fixed_colorbar.setShortcut(QtGui.QApplication.translate("ColorbarDialog", "F", None, QtGui.QApplication.UnicodeUTF8))
        self.manual_range.setText(QtGui.QApplication.translate("ColorbarDialog", "Manual", None, QtGui.QApplication.UnicodeUTF8))
        self.manual_range.setShortcut(QtGui.QApplication.translate("ColorbarDialog", "M", None, QtGui.QApplication.UnicodeUTF8))
        self.ok_button.setText(QtGui.QApplication.translate("ColorbarDialog", "Ok", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ColorbarDialog", "Max", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("ColorbarDialog", "Min", None, QtGui.QApplication.UnicodeUTF8))

