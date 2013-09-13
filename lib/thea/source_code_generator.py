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
This file contains the library used to create the source code for the plot.

"""
import thea.cube_logic as cl


def generate_code(status, coord_indices):
    """
    This function reads in the state of the interface, and then returns the
    source code in the form of a string.

    Args:

    * status
        Dictionary containing the options that have been selected by the user.

    * coord_indices
        List containing ints representing the indices to collapse the cube
        onto, or None if that coord is not to be collapsed.
        For example, if there is a cube with coordinates
        [time, height, lat, lon], and you want collapse the cube onto the
        3rd point in height and the 5th in lon, then coord_indices would be
        [None, 3, None, 5]

    Returns:

    * code
        String containing the formatted source code.

    """
    # We first unpack the variables that we will use.
    filename = status['filename']
    cube_index = status['cube index']
    cube = status['cube']
    plot_method = status['plot method']
    projection = status['projection']
    central_longitude = status['central longitude']
    plot_type = status['plot type']
    cmap = status['cmap']
    num_contours = status['num contours']
    contour_labels = status['contour labels']
    colorbar_range = status['colorbar range']
    can_draw_map = status['can draw map']
    cartographic = status['cartographic']
    gridlines = status['gridlines']
    set_global = status['set global']

    # We can now proceed to build up the code section by section.
    code = ""
    code = add_imports(code, can_draw_map, projection, cartographic)
    code = add_get_cube(code, filename, cube_index)
    code = add_reduce_cube(code, cube, coord_indices)
    code = add_projection(code, plot_method, projection, central_longitude)
    code = add_plot(code, cube, plot_method, plot_type, cmap, num_contours,
                    contour_labels, colorbar_range)
    code = add_cartographic(code, plot_method, can_draw_map, cartographic)
    code = add_gridlines(code, plot_method, gridlines, can_draw_map)
    code = add_set_global(code, set_global)
    code = add_show(code)

    return code


def add_imports(code, can_draw_map, projection, cartographic):
    """
    This section add the required imports to the code.

    Args:

    * code
        String containing the current code.

    * can_draw_map
        Boolean describing if the plot is a lat/lon plot.

    * projection
        String containing the name of the projection to be used.

    * cartographic
        Dictionary containing Booleans about whether to plot coastlines,
        country boundaries and rivers

    Returns:

    * code
        String containing the starting code plus the newly added section.

    """
    rivers = cartographic['rivers']
    countries = cartographic['countries']

    code += "import iris\n"
    code += "import iris.quickplot as qplt\n"
    code += "import matplotlib.pyplot as plt\n"

    if can_draw_map:
        # If a map can be drawn, then we might well need cartopy.
        code += "import cartopy\n"
        if projection != 'Automatic':
            code += "import cartopy.crs as ccrs\n"
        if rivers or countries:
            code += "import cartopy.feature as cfeature\n"
    code += "\n\n"

    return code


def add_get_cube(code, filename, cube_index):
    """
    This section adds the code required to load the correct cube to the string,
    and then returns the updated string.

    Args:

    * code
        String containing the current code.

    * filename
        String containing the path to the file where the cube can be found

    * cube_index
        int giving the index of the desired cube within the cube list.

    Returns:

    * code
        String containing the starting code plus the newly added section.

    """
    code += "cube_list = iris.load('{}')\n".format(filename)
    code += "cube = cube_list[{}]\n".format(cube_index)

    code += "\n"

    return code


def add_reduce_cube(code, cube, coord_indices):
    """
    The function adds the code needed to collapse the cube to the string, and
    then returns the updated string.

    Args:

    * code
        String containing the current code.

    * cube
        The cube that you wish to reduce and plot.

    * coord_indices
        List containing ints representing the indices to collapse the cube
        onto, or None if that coord is not to be collapsed.
        For example, if there is a cube with coordinates
        [time, height, lat, lon], and you want collapse the cube onto the
        3rd point in height and the 5th in lon, then coord_indices would be
        [None, 3, None, 5]

    Returns:

    * code
        String containing the starting code plus the newly added section.

    """
    # If the code has either 1 or 2 dimensions, then there is no need to
    # extract, but we still define sub cube, as this is what the plots refer
    # to.
    if cube.ndim <= 2:
        code += "sub_cube = cube\n"

    else:
        # If we do need to reduce the cube, then we do so as follows;
        code += "sub_cube = cube["

        # This converts [None, 3, None, 5] to [:,3,:,5].
        for index, coord_index in enumerate(coord_indices):
            if coord_index is None:
                code += ":"
            else:
                code += str(coord_index)

            if index != (len(coord_indices) - 1):
                code += ","

        code += "]\n"
        # We now have a line in the form sub_cube = cube[:,3,:,5]

    code += "\n"

    return code


def add_projection(code, plot_method, projection, central_longitude):
    """
    This method adds the code required to set the projection of the plot to
    the string, and then returns the string.

    Args:

    * code
        String containing the current code.

    * plot_method
        String holding the users choice of plotting using either quickplot or
        simply plotting from the data array.

    * projection
        String holding the projection to be used for the plot. Can be any of
        the projections usable in Cartopy, or Automatic.

    * central_longitude
        Double representing the longitude to be positioined in the centre of
        the plot.

    Returns:

    * code
        String containing the starting code plus the newly added section.

    """
    if plot_method == "using quickplot":
        if projection == "Automatic":
            pass
        else:
            # We ensure that the string is in the same form as the names that
            # Cartopy gives the projections by removing the spaces.
            projection = projection.replace(" ", "")
            code += "ax = plt.axes(projection=ccrs.{}".format(projection)
            # These projections do not have a central longitude argument.
            no_central_long_arg = ['OSGB', 'OSNI', 'EuroPP', 'Gnomonic',
                                   'Rotated Pole', 'Automatic']
            if not projection in no_central_long_arg:
                # Add in the central longitude argument iff it exists.
                code += "(central_longitude={})".format(central_longitude)
            code += ")\n"
            code += "\n"
    return code


def add_plot(code, cube, plot_method, plot_type, cmap, num_contours,
             contour_labels, colorbar_range):
    """
    This method adds the code required to make the plot of the cube to the
    string, and then returns the string.

    Args:

    * code
        String containing the current code.

    * cube
        The cube that you wish to reduce and plot.

    * plot_method
        String holding the users choice of plotting using either quickplot or
        simply plotting from the data array.

    * plot_type
        String holding the type of plot to be used. Choose from pcolormesh,
        Contour and Contourf.

    * cmap
        String representing the colormap to be used. Can be any of the Brewer
        Colormaps supported by Iris, or Automatic.

    * num_contour
        int holding the number of contours to be plotted.

    * contour_labels
        Boolean representing whether the contours on a Contour plot (not
        contourf) should be labeled.

    * colorbar_range
        Dictionary containing ints representing the max and min to which the
        colorbar will be set.

    Returns:

    * code
        String containing the starting code plus the newly added section.

    """
    colorbar_max = colorbar_range['max']
    colorbar_min = colorbar_range['min']

    if cube.ndim == 1:
        if plot_method == "using quickplot":
            code += "qplt.plot(sub_cube)\n"
        else:
            code += "plt.plot(sub_cube.data)\n"

    else:

        levels = cl.get_levels(cube, colorbar_max, colorbar_min, num_contours)
        colors = None if cmap == "Automatic" else "'{}'".format(cmap)

        if plot_method == "using quickplot":

            if plot_type == "Filled Contour":
                code += "qplt.contourf(sub_cube, {}, cmap={}, levels={},"\
                    .format(num_contours, colors, levels)
                code += " vmax={}, vmin={})\n".format(
                    colorbar_max, colorbar_min)

            elif plot_type == "Contour":
                code += "im = qplt.contour(sub_cube, {}, cmap={},".format(
                    num_contours, colors)
                code += " levels={}, vmax={}, vmin={})\n".format(
                    levels, colorbar_max, colorbar_min)
                if contour_labels:
                    code += "plt.clabel(im, inline=1, fontsize=8)\n"

            else:
                code += "qplt.pcolormesh(sub_cube, cmap={}, vmax={}, "\
                    .format(colors, colorbar_max)
                code += "vmin={})\n".format(colorbar_min)

        else:

            if plot_type == "Filled Contour":
                code += "im = plt.contourf(sub_cube.data, {}, cmap={},"\
                    .format(num_contours, colors)
                code += " levels={}, vmax={}, vmin={})\n".format(
                    levels, colorbar_max, colorbar_min)

            elif plot_type == "Contour":
                code += "im = plt.contour(sub_cube.data, {}, cmap={}," \
                    .format(num_contours, colors)
                code += " levels={}, vmax={}, vmin={})\n".format(
                    levels, colorbar_max, colorbar_min)
                if contour_labels:
                    code += "plt.clabel(im, inline=1, fontsize=8)\n"

            else:
                code += "im = plt.pcolormesh(sub_cube.data, cmap={},"\
                    .format(colors, colorbar_max)
                code += " vmax={}, vmin={})\n".format(
                    colorbar_max, colorbar_min)

            if plot_type != "Contour":
                code += "bar = plt.colorbar(im)\n"
    code += "\n"

    return code


def add_cartographic(code, plot_method, can_draw_map, cartographic):
    """
    This function adds the code required to add coastlines, country boundaries
    and rivers to the plot, and then returns the updated string.

    Args:

    * code
        String containing the current code.

    * plot_method
        String holding the users choice of plotting using either quickplot or
        simply plotting from the data array.

    * can_draw_map
        See iris.plot._can_draw_map(). This Boolean represents whether or not
        a plot is lat/long.

    * cartographic
        Dictionary containing Booleans about whether to plot coastlines,
        country boundaries and rivers

    Returns:

    * code
        String containing the starting code plus the newly added section.

    """
    coastlines = cartographic['coastlines']
    countries = cartographic['countries']
    rivers = cartographic['rivers']

    if plot_method == "using quickplot":
        if can_draw_map:
            if coastlines:
                code += "plt.gca().coastlines()\n"
                code += "\n"
            if countries:
                code += "countries = cfeature.NaturalEarthFeature("
                code += "   category='cultural',\n"
                code += "   name='admin_0_countries',\n"
                code += "   scale='50m',\n"
                code += "   facecolor='none')\n"
                code += "plt.gca().add_feature(countries)\n"
                code += "\n"
            if rivers:
                code += "plt.gca().add_feature(cfeature.RIVERS)\n"
                code += "plt.gca().add_feature(cfeature.LAKES)\n"
                code += "\n"
    return code


def add_gridlines(code, plot_method, gridlines, can_draw_map):
    """
    This function add the code required to add gridlines to the plot, and
    then returns the updated string.

    Args:

    * code
        String containing the current code.

    * gridlines
        Boolean holding whether or not gridlines are desired.

    * can_draw_map
        See iris.plot._can_draw_map(). This Boolean represents whether or not
        a plot is lat/long.

    * projection
        String holding the projection to be used for the plot. Can be any of
        the projections usable in Cartopy, or Automatic.

    Returns:

    * code
        String containing the starting code plus the newly added section.

    """
    if gridlines:
        if can_draw_map and plot_method == "using quickplot":
            code += "try:\n"
            code += "    grid = plt.gca().gridlines(draw_labels=True)\n"
            code += "    grid.xlabels_top = False\n"
            code += "except TypeError:\n"
            code += "    grid = plt.gca().gridlines(draw_labels=False)\n"
        else:
            code += "plt.gca().grid(True)\n"
        code += "\n"

    return code


def add_set_global(code, set_global):
    """
    This section adds the code required to call set_global() to the string, and
    then returns the updated string.

    Args:

    * code
        String containing the current code.

    * set_global
        Boolean representing whether or not the set global command has been
        called.

    Returns:

    * code
        String containing the starting code plus the newly added section.

    """
    if set_global:
        code += "plt.gca().set_global()\n"
        code += "\n"

    return code


def add_show(code):
    """
    This function adds the code required to display the plot in a window to the
    string, and then returns the updated string.

    Args:

    * code
        String containing the current code.

    Returns:

    * code
        String containing the starting code plus the newly added section.

    """
    code += "plt.show()"

    return code
