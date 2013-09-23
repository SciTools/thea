# -*- coding: iso-8859-1 -*-
#
# (C) British Crown Copyright 2013, Met Office
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
#    Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
#    Neither the name of the Met Office nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.
#
# This file is part of Thea.

"""
This file contains the ColorbarOptions Class

This Class is a Dialog box which gives users some options about what the range
of the colorbar should be.

"""
from PySide import QtGui

from thea.colorbar_dialog_layout import Ui_ColorbarDialog


class ColorbarOptions(QtGui.QDialog, Ui_ColorbarDialog):
    """
    This class controls the colorbar Range selection dialog box.

    The majority of the code for this class was generated from Qt,
    and is called using the setupUi command. This code can be found
    in ColorbarRange.py

    """
    def __init__(self):
        super(ColorbarOptions, self).__init__()
        self.setupUi(self)
        self.set_actions()

    def set_actions(self):
        """
        Here we define what happens when the various objects are activated

        """
        self.autoselect_range.clicked.connect(self.autoselect_clicked)
        self.fixed_colorbar.clicked.connect(self.fixed_colorbar_clicked)
        self.manual_range.clicked.connect(self.manual_clicked)

    def autoselect_clicked(self):
        """
        This method defines what occurs when the autoselect button is clicked.

        """
        # If the checkbox originally unchecked (and so is now checked), then we
        # let it be checked, and ensure that the others are not
        if self.autoselect_range.isChecked():
            self.fixed_colorbar.setChecked(False)
            self.manual_range.setChecked(False)
        # If it were checked when it was clicked, then we let it be unchecked,
        # and we check fixed_colorbar isntead.
        else:
            self.fixed_colorbar.setChecked(True)

    def fixed_colorbar_clicked(self):
        """
        This method defines what occurs when fixed_colorbar is clicked.

        """
        if self.fixed_colorbar.isChecked():
            self.autoselect_range.setChecked(False)
            self.manual_range.setChecked(False)
        else:
            self.autoselect_range.setChecked(True)

    def manual_clicked(self):
        """
        This method defines what occurs when manual is clicked.

        """
        if self.manual_range.isChecked():
            self.autoselect_range.setChecked(False)
            self.fixed_colorbar.setChecked(False)
        else:
            self.autoselect_range.setChecked(True)

    def get_max_min(self):
        """
        Returns the values currently displayed for maximum and minimum.

        """
        colorbar_max = self.max_contour.value()
        colorbar_min = self.min_contour.value()

        return colorbar_max, colorbar_min

    def get_colorbar_scheme(self):
        """
        Returns the current method of obtaining the range as a String.

        """
        if self.autoselect_range.isChecked():
            return "auto"
        elif self.fixed_colorbar.isChecked():
            return "fixed"
        else:
            return "manual"

    def set_max_min(self, colorbar_max, colorbar_min):
        """
        Allows for the remote setting of the value of the colorbar.
        """
        if colorbar_max is not None and colorbar_min is not None:
            self.max_contour.setValue(colorbar_max)
            self.min_contour.setValue(colorbar_min)

    def disable_fixed_colorbar(self, ndim):
        """
        Disables the fixed_colorbar option for plots with fewer than 3
        dimensions.

        """
        if ndim == 2:
            self.fixed_colorbar.setEnabled(False)
            if self.fixed_colorbar.isChecked():
                self.fixed_colorbar.setChecked(False)
                self.autoselect_range.setChecked(True)
        else:
            self.fixed_colorbar.setEnabled(True)
