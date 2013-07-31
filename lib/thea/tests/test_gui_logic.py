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

import unittest
import numpy as np
import iris

import thea.gui_logic as gl
import thea.tests.test_cube_logic as tcl


def compare_dict(dictA, dictB):
    for key in dictB.keys():
        if not key in dictA.keys():
            msg = "Key: " + str(key) + " does not exist in dictA"
            return msg
    for key in dictA.keys():
        if not key in dictB.keys():
            msg = "Key: " + str(key) + " does not exist in dictB"
            return msg
        elif not dictA[key] == dictB[key]:
            msg = "dictA: " + str(key) + ": " + str(dictA[key])
            msg += "    dictB: " + str(key) + ": " + str(dictB[key])
            return msg
    return None


class GuiLogicTests(unittest.TestCase):
    """
    This class contains a series of tests designed to ensure that the gui_logic
    class is functioning as intended.

    """
    def test_compare_dict_pass(self):
        dictA = {'one': 1,
                 'two': 2,
                 'three': 3}
        dictB = {'one': 1,
                 'two': 2,
                 'three': 3}
        result = compare_dict(dictA, dictB)
        self.assertIsNone(result)

    def test_compare_dict_fail_element_wrong(self):
        dictA = {'one': 1,
                 'two': 2,
                 'three': 3}
        dictB = {'one': 1,
                 'two': 6,
                 'three': 3}
        result = compare_dict(dictA, dictB)
        self.assertEqual(result, "dictA: two: 2    dictB: two: 6")

    def test_compare_dict_fail_A_too_large(self):
        dictA = {'one': 1,
                 'two': 2,
                 'three': 3}
        dictB = {'one': 1,
                 'two': 2}
        result = compare_dict(dictA, dictB)
        self.assertEqual(result, "Key: three does not exist in dictB")

    def test_compare_dict_fail_B_too_large(self):
        dictA = {'one': 1,
                 'two': 2}
        dictB = {'one': 1,
                 'two': 2,
                 'three': 3}
        result = compare_dict(dictA, dictB)
        self.assertEqual(result, "Key: three does not exist in dictA")

    def test_get_dim_names_1d(self):
        cube = tcl.setup_1d_cube()
        names = gl.get_dim_names(cube)
        self.assertEqual(names, ["time"])

    def test_get_dim_names_7d(self):
        cube = tcl.setup_7d_anonymous_cube()
        names = gl.get_dim_names(cube)
        self.assertEqual(names, ["*ANONYMOUS*0", "*ANONYMOUS*1",
                                 "*ANONYMOUS*2", "*ANONYMOUS*3",
                                 "*ANONYMOUS*4", "*ANONYMOUS*5",
                                 "*ANONYMOUS*6"])

    def test_get_remaining_dims_4d(self):
        cube = tcl.setup_4d_cube()
        names = gl.get_dim_names(cube)
        used_dims = (names[2], names[0], names[3])
        remaining_dims = gl.get_remaining_dims(names, used_dims)
        self.assertEqual(remaining_dims, [names[1]])

    def test_get_remaining_dims_7d_anonymous(self):
        cube = tcl.setup_7d_anonymous_cube()
        names = gl.get_dim_names(cube)
        used_dims = (names[5], names[3], names[0])
        remaining_dims = gl.get_remaining_dims(names, used_dims)
        self.assertEqual(remaining_dims, [names[1], names[2], names[4],
                         names[6]])

    def test_get_dim_index(self):
        cube = tcl.setup_4d_cube()
        names = gl.get_dim_names(cube)
        dim = "model_level_number"
        index = gl.get_dim_index(dim, names)
        expected_index = 1
        self.assertEqual(index, expected_index)

    def test_get_dim_values_4d(self):
        cube = tcl.setup_4d_cube()
        names = gl.get_dim_names(cube)
        values = gl.get_coord_values(cube, "grid_latitude", names)
        expected_values = cube.coord("grid_latitude").points
        self.assertEqual(all(values), all(expected_values))

    def test_get_dim_values_date_time(self):
        cube = tcl.setup_4d_cube()
        names = gl.get_dim_names(cube)
        values = gl.get_coord_values(cube, "time", names)
        points = cube.coord("time").points
        coord = cube.coord("time")
        expected_values = [coord.units.num2date(point) for point in points]
        self.assertEqual(all(values), all(expected_values))

    def test_get_dim_values_anonymous_dim(self):
        cube = tcl.setup_7d_anonymous_cube()
        names = gl.get_dim_names(cube)
        values = gl.get_coord_values(cube, "*ANONYMOUS*4", names)
        expected_values = (range(5))
        self.assertEqual(values, expected_values)

    def test_get_enabled_no_cube_pcolormesh(self):
        cube = None
        dim_1_name = None
        dim_2_name = None
        status = {'cube loaded': False,
                  'plot method': 'from data array',
                  'plot type': 'pcolormesh',
                  'cube': cube,
                  'dim 1 name': dim_1_name,
                  'dim 2 name': dim_2_name,
                  'projection': 'Automatic'}
        state = gl.get_enabled(status)
        expected_state = {'previous': False,
                          'next': False,
                          'cartographic': False,
                          'labels': False,
                          'colorbar': False,
                          'plot type': True,
                          'colormap': True,
                          'contour slider': False,
                          'third dim': False,
                          'source code': False,
                          'central longitude': False,
                          'update': False}
        difference = compare_dict(state, expected_state)
        self.assertIsNone(difference)

    def test_get_enabled_no_cube_contour(self):
        cube = None
        dim_1_name = None
        dim_2_name = None
        status = {'cube loaded': False,
                  'plot method': 'using quickplot',
                  'plot type': 'Contour',
                  'cube': cube,
                  'dim 1 name': dim_1_name,
                  'dim 2 name': dim_2_name,
                  'projection': 'Automatic'}
        state = gl.get_enabled(status)
        expected_state = {'previous': False,
                          'next': False,
                          'cartographic': True,
                          'labels': True,
                          'colorbar': False,
                          'plot type': True,
                          'colormap': True,
                          'contour slider': True,
                          'third dim': False,
                          'source code': False,
                          'central longitude': False,
                          'update': False}
        difference = compare_dict(state, expected_state)
        self.assertIsNone(difference)

    def test_get_enabled_1d_pcolormesh_array(self):
        cube = tcl.setup_1d_cube()
        dim_1_name = 'time'
        dim_2_name = None
        status = {'cube loaded': True,
                  'plot method': 'from data array',
                  'plot type': 'pcolormesh',
                  'cube': cube,
                  'dim 1 name': dim_1_name,
                  'dim 2 name': dim_2_name,
                  'projection': 'Automatic'}
        state = gl.get_enabled(status)
        expected_state = {'previous': False,
                          'next': False,
                          'source code': True,
                          'cartographic': False,
                          'labels': False,
                          'colorbar': False,
                          'plot type': False,
                          'colormap': False,
                          'contour slider': False,
                          'third dim': False,
                          'central longitude': False,
                          'update': True}
        difference = compare_dict(state, expected_state)
        self.assertIsNone(difference)

    def test_get_enabled_1d_contour_qptl(self):
        cube = tcl.setup_1d_cube()
        dim_1_name = 'time'
        dim_2_name = None
        status = {'cube loaded': True,
                  'plot method': 'using quickplot',
                  'plot type': 'Contour',
                  'cube': cube,
                  'dim 1 name': dim_1_name,
                  'dim 2 name': dim_2_name,
                  'projection': 'Automatic'}
        state = gl.get_enabled(status)
        expected_state = {'previous': False,
                          'next': False,
                          'source code': True,
                          'cartographic': False,
                          'labels': False,
                          'colorbar': False,
                          'plot type': False,
                          'colormap': False,
                          'contour slider': False,
                          'third dim': False,
                          'central longitude': False,
                          'update': True}
        difference = compare_dict(state, expected_state)
        self.assertIsNone(difference)

    def test_get_enabled_2d_filled_contour_qptl(self):
        cube = tcl.setup_2d_cube()
        dim_1_name = 'latitude'
        dim_2_name = 'longitude'
        status = {'cube loaded': True,
                  'plot method': 'using quickplot',
                  'plot type': 'Filled Contour',
                  'cube': cube,
                  'dim 1 name': dim_1_name,
                  'dim 2 name': dim_2_name,
                  'projection': 'Automatic'}
        state = gl.get_enabled(status)
        expected_state = {'previous': False,
                          'next': False,
                          'source code': True,
                          'cartographic': True,
                          'labels': False,
                          'colorbar': True,
                          'plot type': True,
                          'colormap': True,
                          'contour slider': True,
                          'third dim': False,
                          'central longitude': False,
                          'update': True}
        difference = compare_dict(state, expected_state)
        self.assertIsNone(difference)

    def test_get_enabled_2d_pcolormesh_data(self):
        cube = tcl.setup_2d_cube()
        dim_1_name = 'latitude'
        dim_2_name = 'longitude'
        status = {'cube loaded': True,
                  'plot method': 'from data array',
                  'plot type': 'pcolormesh',
                  'cube': cube,
                  'dim 1 name': dim_1_name,
                  'dim 2 name': dim_2_name,
                  'projection': 'Automatic'}
        state = gl.get_enabled(status)
        expected_state = {'previous': False,
                          'next': False,
                          'source code': True,
                          'cartographic': False,
                          'labels': False,
                          'colorbar': True,
                          'plot type': True,
                          'colormap': True,
                          'contour slider': False,
                          'third dim': False,
                          'central longitude': False,
                          'update': True}
        difference = compare_dict(state, expected_state)
        self.assertIsNone(difference)

    def test_get_enabled_4d_contour_data(self):
        cube = tcl.setup_4d_cube()
        dim_1_name = 'grid_latitude'
        dim_2_name = 'grid_longitude'
        status = {'cube loaded': True,
                  'plot method': 'from data array',
                  'plot type': 'Contour',
                  'cube': cube,
                  'dim 1 name': dim_1_name,
                  'dim 2 name': dim_2_name,
                  'projection': 'Automatic'}
        state = gl.get_enabled(status)
        expected_state = {'previous': True,
                          'next': True,
                          'source code': True,
                          'cartographic': False,
                          'labels': True,
                          'colorbar': True,
                          'plot type': True,
                          'colormap': True,
                          'contour slider': True,
                          'third dim': True,
                          'central longitude': False,
                          'update': True}
        difference = compare_dict(state, expected_state)
        self.assertIsNone(difference)

    def test_get_enabled_4d_filled_contour_qplt(self):
        cube = tcl.setup_4d_cube()
        dim_1_name = 'time'
        dim_2_name = 'grid_longitude'
        status = {'cube loaded': True,
                  'plot method': 'using quickplot',
                  'plot type': 'Filled Contour',
                  'cube': cube,
                  'dim 1 name': dim_1_name,
                  'dim 2 name': dim_2_name,
                  'projection': 'Automatic'}
        state = gl.get_enabled(status)
        expected_state = {'previous': True,
                          'next': True,
                          'source code': True,
                          'cartographic': False,
                          'labels': False,
                          'colorbar': True,
                          'plot type': True,
                          'colormap': True,
                          'contour slider': True,
                          'third dim': True,
                          'central longitude': False,
                          'update': True}
        difference = compare_dict(state, expected_state)
        self.assertIsNone(difference)

    def test_can_draw_map_true(self):
        cube = tcl.setup_4d_cube()
        dim_1_name = "grid_longitude"
        dim_2_name = "grid_latitude"
        can_draw_map = gl.get_can_draw_map(cube, dim_1_name, dim_2_name)
        self.assertTrue(can_draw_map)

    def test_can_draw_map_reversed(self):
        cube = tcl.setup_4d_cube()
        dim_1_name = "grid_longitude"
        dim_2_name = "grid_latitude"
        can_draw_map = gl.get_can_draw_map(cube, dim_2_name, dim_1_name)
        self.assertTrue(can_draw_map)

    def test_can_draw_map_false(self):
        cube = tcl.setup_4d_cube()
        dim_1_name = "grid_longitude"
        dim_2_name = "time"
        can_draw_map = gl.get_can_draw_map(cube, dim_2_name, dim_1_name)
        self.assertFalse(can_draw_map)

    def test_can_draw_map_anonymous(self):
        cube = tcl.setup_7d_anonymous_cube()
        dim_1_name = "*ANONYMOUS*2"
        dim_2_name = "*ANONYMOUS*5"
        can_draw_map = gl.get_can_draw_map(cube, dim_2_name, dim_1_name)
        self.assertFalse(can_draw_map)


if __name__ == '__main__':
    unittest.main()
