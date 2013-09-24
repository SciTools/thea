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
This file contains the Viewer Class

This Class is a Dialog box which allows the user to see the source code that
would generate the current image.

"""
from PySide import QtGui

from thea.source_code_dialog_layout import Ui_Dialog


class Viewer(QtGui.QDialog, Ui_Dialog):
    """
    The Viewer Class is a dialog box which gives the user the chance to view
    source code that would generate the plot, and then to save this code. The
    class extends the QDialog class, and includes codeViewInterface.Ui_Dialog,
    from where it will get the layout.

    """
    def __init__(self):
        """
        On start, we setup the layout of the dialog, and define the action
        of the save_button.

        """
        super(Viewer, self).__init__()
        self.setupUi(self)
        self.save_button.clicked.connect(self.save)

    def set_code(self, code):
        """
        This method sets the instance variable of the code, and displays the
        source code by setting it as the text in the code_browser object.

        Args:

        * code
            The code that should be displayed in the browser.

        """
        self.code = code
        self.code_browser.setText(code)

    def save(self):
        """
        This method opens the save dialog, allowing you to save the code in a
        file anywhere on the system.

        """
        filename, _ = QtGui.QFileDialog.getSaveFileName()

        with open(filename, 'w') as fh:
            fh.write(self.code)
