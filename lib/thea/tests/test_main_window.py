# -*- coding: iso-8859-1 -*-
#
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

import sys
import unittest

from PySide import QtGui
import iris

import thea.main_window as main_window


class MainWindowTests(unittest.TestCase):

    def test_correct_arguments_no_cube(self):
        window = main_window.MainWindow(None)
        status = window.get_status()
        keys_given = status.keys()
        keys_expected = ('cube', 'plot method', 'plot type', 'projection',
                         'cmap', 'num contours', 'cartographic', 'gridlines',
                         'contour labels', 'colorbar range', 'dim indices',
                         'slice index', 'collapsed indices', 'can draw map')
        for key in keys_expected:
            if not key in keys_given:
                missing = key
                break
            missing = None
        self.assertIsNone(missing)

    def test_correct_arguments_passed_update(self):
        window = main_window.MainWindow(None)
        cubes = iris.load(iris.sample_data_path('air_temp.pp'))
        window.cubes = cubes
        window.cube_loaded = True
        window.filename = 'some string'
        window.select_cube.addItem('cube')
        window.select_cube.setCurrentIndex(0)
        window.select_dimension_1.addItem('coord')
        window.select_dimension_1.setCurrentIndex(0)
        status = window.get_status()
        keys_given = status.keys()
        keys_expected = ('cube', 'plot method', 'plot type', 'projection',
                         'cmap', 'num contours', 'cartographic', 'gridlines',
                         'contour labels', 'colorbar range', 'dim indices',
                         'slice index', 'collapsed indices', 'can draw map')
        for key in keys_expected:
            if not key in keys_given:
                missing = key
                break
            missing = None
        self.assertIsNone(missing)

    def test_correct_dim_indices(self):
        window = main_window.MainWindow(None)
        cubes = iris.load(iris.sample_data_path('air_temp.pp'))
        window.cubes = cubes
        window.cube_loaded = True
        window.filename = 'some string'
        window.select_cube.addItem('cube')
        window.select_cube.setCurrentIndex(0)
        window.select_dimension_1.addItem('coord')
        window.select_dimension_1.setCurrentIndex(0)
        status = window.get_status()
        keys_given = status['dim indices'].keys()
        keys_expected = ('dim 1 index', 'dim 2 index', 'sliced dim index')
        for key in keys_expected:
            if not key in keys_given:
                missing = key
                break
            missing = None
        self.assertIsNone(missing)

    def test_correct_colorbar_range(self):
        window = main_window.MainWindow(None)
        cubes = iris.load(iris.sample_data_path('air_temp.pp'))
        window.cubes = cubes
        window.cube_loaded = True
        window.filename = 'some string'
        window.select_cube.addItem('cube')
        window.select_cube.setCurrentIndex(0)
        window.select_dimension_1.addItem('coord')
        window.select_dimension_1.setCurrentIndex(0)
        status = window.get_status()
        keys_given = status['colorbar range'].keys()
        keys_expected = ('max', 'min')
        for key in keys_expected:
            if not key in keys_given:
                missing = key
                break
            missing = None
        self.assertIsNone(missing)

    def test_correct_cartographic(self):
        window = main_window.MainWindow(None)
        cubes = iris.load(iris.sample_data_path('air_temp.pp'))
        window.cubes = cubes
        window.cube_loaded = True
        window.filename = 'some string'
        window.select_cube.addItem('cube')
        window.select_cube.setCurrentIndex(0)
        window.select_dimension_1.addItem('coord')
        window.select_dimension_1.setCurrentIndex(0)
        status = window.get_status()
        keys_given = status['cartographic'].keys()
        keys_expected = ('countries', 'coastlines', 'rivers')
        for key in keys_expected:
            if not key in keys_given:
                missing = key
                break
            missing = None
        self.assertIsNone(missing)


def main():
    app = QtGui.QApplication(sys.argv)
    unittest.main()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
