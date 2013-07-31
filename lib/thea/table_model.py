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
#
# This file is part of Thea.

"""
This file contains the TableModel Class.

The TableModel works with Qt's QTableView class in a model-viewer relationship,
to display the data contained within the current slice.

"""
from PySide import QtCore


class TableModel(QtCore.QAbstractTableModel):
    """
    The TableModel class is designed to work with the Qt QTableView Class.
    The QTableView is the Viewer for the table model created here.
    The QTableView is passed the data to display by the TableModel, which
    is where all of the calculation and data can be found.

    """
    def __init__(self, data_in, horiz_header_data, vert_header_data, *args):
        """
        We define the instance variables from the arguments given

        Args:

        * data_in
            np.array containing the data that you wish to display.

        * horiz_header_data
            The values with which to fill the column headers

        * vert_header_data
            The values with which to fill the row headers

        """
        QtCore.QAbstractTableModel.__init__(self, *args)
        self.array_data = data_in
        self.horiz_header_data = horiz_header_data
        self.vert_header_data = vert_header_data

    def rowCount(self, _):
        """
        Returns the required number of rows

        """
        return len(self.array_data)

    def columnCount(self, _):
        """
        Returns the required number of columns

        """
        try:
            return len(self.array_data[0])
        except TypeError:
            return 1

    def data(self, index, role):
        """
        Returns the data at the given index

        """
        if not index.isValid():
            return None
        elif role != QtCore.Qt.DisplayRole:
            return None
        try:
            return self.array_data[index.row()][index.column()]
        except TypeError:
            return self.array_data[index.row()]

    def headerData(self, index, orientation, role):
        """
        Returns the specified row or column data.

        """
        if orientation == QtCore.Qt.Horizontal and \
                role == QtCore.Qt.DisplayRole:
            return str(self.horiz_header_data[index])
        elif orientation == QtCore.Qt.Vertical \
                and role == QtCore.Qt.DisplayRole:
            return str(self.vert_header_data[index])
        else:
            return None
