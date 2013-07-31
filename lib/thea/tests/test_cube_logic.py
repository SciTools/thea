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

import unittest

import cartopy.crs as ccrs
import iris
import iris.quickplot as qplt
import matplotlib.pyplot as plt
import numpy as np

import thea.cube_logic as cl


def setup_1d_cube():
    cube = iris.load_cube(iris.sample_data_path('SOI_Darwin.nc'))
    return cube


def setup_2d_cube():
    cube = iris.load_cube(iris.sample_data_path('air_temp.pp'))
    return cube


def setup_3d_cube():
    cube = iris.load_cube(iris.sample_data_path('A1B_north_america.nc'))
    return cube


def setup_4d_cube():
    cube = iris.load(iris.sample_data_path('uk_hires.pp'))[0]
    return cube


def setup_7d_anonymous_cube():
    data = np.arange(0, 5*5*5*5*5*5*5)
    data = np.reshape(data, [5, 5, 5, 5, 5, 5, 5])
    cube = iris.cube.Cube(data)
    return cube


class CubeLogicTests(unittest.TestCase):
    """
    This class contains a set of tests designed to check that the cube_logic
    module is working as intended.

    """
    def setup_update(self):
        cartographic = {'coastlines': True,
                        'countries': False,
                        'rivers': False}
        colorbar_range = {'max': None,
                          'min': None}
        status = {'plot method': "using quickplot",
                  'plot type': "Contour",
                  'projection': "Automatic",
                  'central longitude': 0.0,
                  'cmap': None,
                  'num contours': 25,
                  'cartographic': cartographic,
                  'gridlines': False,
                  'contour labels': False,
                  'colorbar range': colorbar_range,
                  'can draw map': False,
                  'dim 1 name': 'x',
                  'dim 2 name': 'y'}
        return status

    def test_cube_reduction_4d(self):
        cube = setup_4d_cube()
        dim_indices = {'dim 1 index': 2,
                       'dim 2 index': 0,
                       'sliced dim index': 1}
        collapsed_indices = [1]
        new_cube = cl.get_sub_cube(cube, dim_indices, collapsed_indices)
        expected_cube = cube[:, :, :, 1]
        self.assertEqual(new_cube, expected_cube)

    def test_cube_reduction_7d(self):
        cube = setup_7d_anonymous_cube()
        dim_indices = {'dim 1 index': 4,
                       'dim 2 index': 0,
                       'sliced dim index': 6}
        collapsed_indices = [0, 3, 4, 2]
        new_cube = cl.get_sub_cube(cube, dim_indices, collapsed_indices)
        expected_cube = cube[:, 0, 3, 4, :, 2, :]
        self.assertEqual(new_cube, expected_cube)

    def test_update_sub_cube_1d(self):
        cube = setup_1d_cube()
        status = self.setup_update()
        dim_indices = {'dim 1 index': 0,
                       'dim 2 index': -1,
                       'sliced dim index': -1}
        status['cube'] = cube
        status['dim indices'] = dim_indices
        status['slice index'] = -1
        status['collapsed indices'] = []

        sub_cube, _ = cl.update(status)
        self.assertEqual(sub_cube, cube)

    def test_update_sub_cube_2d(self):
        cube = setup_2d_cube()
        status = self.setup_update()
        dim_indices = {'dim 1 index': 1,
                       'dim 2 index': 0,
                       'sliced dim index': -1}
        status['cube'] = cube
        status['dim indices'] = dim_indices
        status['slice index'] = -1
        status['collapsed indices'] = []

        sub_cube, _ = cl.update(status)
        self.assertEqual(sub_cube, cube)

    def test_update_sub_cube_3d(self):
        cube = setup_3d_cube()
        status = self.setup_update()
        dim_indices = {'dim 1 index': 1,
                       'dim 2 index': 0,
                       'sliced dim index': 2}
        status['cube'] = cube
        status['dim indices'] = dim_indices
        status['slice index'] = 2
        status['collapsed indices'] = []

        sub_cube, _ = cl.update(status)
        expected_cube = cube[:, :, 2]
        self.assertEqual(sub_cube, expected_cube)

    def test_update_sub_cube_4d(self):
        cube = setup_4d_cube()
        status = self.setup_update()
        dim_indices = {'dim 1 index': 1,
                       'dim 2 index': 0,
                       'sliced dim index': 2}
        status['cube'] = cube
        status['dim indices'] = dim_indices
        status['slice index'] = 2
        status['collapsed indices'] = [3]

        sub_cube, _ = cl.update(status)
        expected_cube = cube[:, :, 2, 3]
        self.assertEqual(sub_cube, expected_cube)

    def test_update_sub_cube_7d(self):
        cube = setup_7d_anonymous_cube()
        status = self.setup_update()
        dim_indices = {'dim 1 index': 4,
                       'dim 2 index': 2,
                       'sliced dim index': 6}
        status['cube'] = cube
        status['dim indices'] = dim_indices
        status['slice index'] = 2
        status['collapsed indices'] = [2, 1, 2, 4]

        sub_cube, _ = cl.update(status)
        expected_cube = cube[2, 1, :, 2, :, 4, 2]
        self.assertEqual(sub_cube, expected_cube)

    def test_colormap_none(self):
        colormap = cl.get_colormap("Automatic")
        self.assertIsNone(colormap)

    def test_colormap_brewer(self):
        colormap = cl.get_colormap("brewer_RdBu_11")
        self.assertEqual(colormap, "brewer_RdBu_11")

    def test_fixed_colormap(self):
        cube = setup_7d_anonymous_cube()
        dim_indices = {'dim 1 index': 1,
                       'dim 2 index': 4,
                       'sliced dim index': 0}
        collapsed_indices = [2, 3, 4, 0]
        maximum, minimum = cl.set_fixed_colorbar(
            cube, dim_indices, collapsed_indices)
        max_min = (maximum, minimum)
        expected = (76745, 1645)
        self.assertEqual(max_min, expected)

    def test_find_max_min(self):
        cube = setup_7d_anonymous_cube()
        maximum, minimum = cl.find_max_min(cube)
        max_min = (maximum, minimum)
        expected = ((5*5*5*5*5*5*5) - 1, 0)
        self.assertEqual(max_min, expected)

    def test_check_extent_without_quickplot(self):
        cube = setup_2d_cube()
        plt.contourf(cube.data)
        set_global = cl.check_extent("from data array", True)
        self.assertFalse(set_global)

    def test_check_extent_no_map(self):
        cube = setup_3d_cube()[0]
        qplt.contourf(cube)
        set_global = cl.check_extent("using quickplot", False)
        self.assertFalse(set_global)

    def test_check_extent_not_required(self):
        cube = setup_2d_cube()
        qplt.contourf(cube)
        set_global = cl.check_extent("using quickplot", True)
        self.assertFalse(set_global)

    def test_check_extent_required(self):
        cube = setup_2d_cube()
        plt.axes(projection=ccrs.Stereographic())
        qplt.pcolormesh(cube)
        set_global = cl.check_extent("using quickplot", True)
        self.assertTrue(set_global)

    def test_adding_labels_lat_long(self):
        cube = setup_2d_cube()
        axis_labels = ('latitude', 'longitude')
        xlabel, ylabel = cl.sort_axis_labels(cube, axis_labels)
        self.failUnless(xlabel == 'longitude', ylabel == 'latitude')


if __name__ == '__main__':
    unittest.main()
