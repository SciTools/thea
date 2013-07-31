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
This file contains a Library of functions, which are used to poll the cube to
obtain data to fill the combo boxes with, and to determin which elements
of the interface should be enabled at any point in time.

"""
import iris
import iris.plot as iplt


def get_dim_names(cube):
    """
    Finds the names of the dimension Coordinates in the cube, and returns a
    list of these names. If the coordinate is anonymous, it will generate a
    name as *ANONYMOUS*{} (where {} is replaced by a number, making the name
    unique)

    Args:

    * cube
        The cube for which the names are desired.

    Returns:

    * headers
        List of Strings holding the names of the dimension coordinates in the
        cube, including any anonymous dimensions.

    """
    dim_names = [set() for dim in xrange(cube.ndim)]

    for dim in xrange(len(cube.shape)):
        for coord in cube.coords(contains_dimension=dim, dim_coords=True):
            dim_names[dim].add(coord.name())

    dim_names = [sorted(names, key=iris.cube.sorted_axes)
                 for names in dim_names]

    headers = []
    for dim in xrange(len(cube.shape)):
        headers.append(''.join(dim_names[dim] or ['*ANONYMOUS*' + str(dim)]))

    return headers


def get_remaining_dims(dim_names, used_dims):
    """
    Finds the names of any coords which are in the list of dim_names, but not
    in the list of used_dims.

    In the program, this is used to find the coordinates which have not been
    accounted for already by the select_dimension boxes and the
    select_slice_dim box.

    Args:

    * dim_names
        List of Strings.

    * used_dims
        List of Strings.

    Returns:

    * unused_dims
        List of Strings containing the names that were found in dim_names but
        not in used_dims

    """
    unused_dims = [name for name in dim_names if name not in used_dims]
    return unused_dims


def get_dim_index(dim_name, all_dim_names):
    """
    Returns the index of the coordinate.

    For example, if a cube has coordinates [time, lat, lon], then time has an
    index of 0, lat has an index of 1, lon has an index of 2.

    Args:

    * dim_name
        String representing the name of the coordinate whose index is desired.

    * all_dim_names
        list of Strings holding the names of all of the coords in the cube,
        as found by get_dim_names()

    Returns

    * index
        Int containing the index of the coordinate.

    """
    for index, dim in enumerate(all_dim_names):
        if dim_name == dim:
            return index
    return None


def get_coord_values(cube, dim, dim_names):
    """
    Returns coord.points, or, if the dimension is anonymous, and so does not
    have coord.points, returns a list representing the index of the points.

    Args:

    * cube
        The cube to which the coordinate belongs

    * dim
        String representing the dimension for which you want to obtain
        coord.points.

    * dim_names
        List of Strings containg all of the dimension names as obtained from
        get_dim_names()

    """
    try:
        coord = cube.coord(dim)
        if coord.units.is_time_reference():
            data = []
            for point in coord.points:
                data.append(coord.units.num2date(point))
        else:
            data = cube.coord(dim).points
    except iris.exceptions.CoordinateNotFoundError:
        dim_index = get_dim_index(dim, dim_names)
        dim_size = cube.shape[dim_index]
        data = [i for i in xrange(dim_size)]
    return data


def get_enabled(status):
    """
    Contains the logic to decide which elements of the interface will be
    disabled at any time. Returns a dictionary containing this information.

    Args:

    * status
        A dictionary containing the complete current state of which options
        have been selected in the main window.

    Returns:

    * state
        A dictionary of Booleans describing which parts of the interface
        should be enabled, based on the current options chosen and cube
        present.

    """
    state = {'previous': True,
             'next': True,
             'source code': True,
             'cartographic': True,
             'labels': False,
             'colorbar': True,
             'plot type': True,
             'central longitude': True,
             'colormap': True,
             'contour slider': True,
             'third dim': True,
             'update': True}

    if status['plot type'] == "pcolormesh":
        state['contour slider'] = False

    elif status['plot type'] == "Contour":
        state['labels'] = True

    if not status['cube loaded']:
        state['source code'] = False
        state['third dim'] = False
        state['next'] = False
        state['previous'] = False
        state['colorbar'] = False
        state['update'] = False

    else:
        cube = status['cube']
        if cube.ndim < 3:
            state['third dim'] = False
            state['next'] = False
            state['previous'] = False

            if cube.ndim == 1:
                state['cartographic'] = False
                state['colorbar'] = False
                state['colormap'] = False
                state['contour slider'] = False
                state['plot type'] = False
                state['labels'] = False

        try:
            can_draw_map = get_can_draw_map(cube, status['dim 1 name'],
                                            status['dim 2 name'])
            state['cartographic'] = can_draw_map
        except AttributeError:
            state['cartographic'] = False

    if status['plot method'] == "from data array":
        state['cartographic'] = False

    state['central longitude'] = state['cartographic']
    no_central_long_arg = ['OSGB', 'OSNI', 'EuroPP', 'Gnomonic',
                           'Rotated Pole', 'Automatic']
    if status['projection'] in no_central_long_arg:
        state['central longitude'] = False

    return state


def get_can_draw_map(cube, dim_1_name, dim_2_name):
    """
    Determines if the plot is a lat/lon plot by calling the iris.plot method
    _can_draw_map([coord1, coord2]). Returns a Boolean.

    Args:

    * cube
        The cube being plotted

    * dim_1_name
        The name of the first axis dimension (obtained from
        MainWindow.select_dimension_1.currentText())

    * dim_2_name
        The name of the second axis dimension.

    Returns:

    * can_draw_map
        Boolean describing if the the plot is lat/lon or not.

    """
    try:
        coord_1 = cube.coord(dim_1_name)
        coord_2 = cube.coord(dim_2_name)

        can_draw_map = iplt._can_draw_map([coord_1, coord_2])
        if not can_draw_map:
            can_draw_map = iplt._can_draw_map([coord_2, coord_1])
    except iris.exceptions.CoordinateNotFoundError:
        can_draw_map = False

    return can_draw_map
