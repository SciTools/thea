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
This file contains a Library, which contains functions that are used to reduce
the cube, get information from the cube and make a plot object from the cube
a set of options.

"""
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import iris.quickplot as qplt
import matplotlib.pyplot as plt
import numpy as np

from thea.gui_logic import get_dim_names


def update(status):
    """
    Called whenever the update button is pressed.

    This function takes the status of the interface of its argument, and
    returns the sub_cube that has been plotted, and whether or not the set
    global method has been used.

    Args:

    * status
        A dictionary representing the complete current state of the interface,
        including the current cube, dimensions to be plotted etc.

    Returns:

    * sub_cube
        The reduced cube that was plotted by this method.

    * set_global
        If the extent of the data is greater than the extent of the projection,
        then set_global is called to ensure that the size of the plot is
        sensible. This variable holds if this method was required.

    """
    # We begin by unpacking the elements of the dictionary that are needed.
    cube = status['cube']
    plot_method = status['plot method']
    plot_type = status['plot type']
    projection = status['projection']
    central_longitude = status['central longitude']
    cmap = status['cmap']
    num_contours = status['num contours']
    cartographic = status['cartographic']
    gridlines = status['gridlines']
    contour_labels = status['contour labels']
    colorbar_range = status['colorbar range']
    dim_indices = status['dim indices']
    slice_index = status['slice index']
    collapsed_indices = status['collapsed indices']
    can_draw_map = status['can draw map']
    axis_labels = (status['dim 1 name'], status['dim 2 name'])

    if cube.ndim == 1:
        # For a 1D cube, no extraction is needed.
        sub_cube = cube
        plot_1d(sub_cube, plot_method, gridlines)

    else:
        if cube.ndim == 2:
            # If the cube is 2D, no extraction is required.
            sub_cube = cube

        else:
            # The cube has at least 3 dimensions.
            # We therefore need to extract a sub-cube to plot.
            sub_cube = get_sub_cube(cube, dim_indices, collapsed_indices)
            new_index = get_correct_index(dim_indices)
            sub_cube = extract_cube(sub_cube, [new_index], [slice_index])

        # The 2D cube can now be plotted.
        plot_2d(sub_cube, plot_method, plot_type, projection,
                central_longitude, cmap, num_contours, cartographic, gridlines,
                contour_labels, colorbar_range, axis_labels)

    set_global = check_extent(plot_method, can_draw_map)

    return sub_cube, set_global


def plot_1d(cube, plot_method, gridlines):
    """
    Produces a plot object for 1D cubes using the quickplot.plot() method or
    the matplotlib.pyplot.plot() method.

    Args:

    * cube
        The 1D cube to be plotted.

    * plot_method
        String holding the users choice of plotting using either quickplot or
        simply plotting from the data array.

    * gridlines
        Boolean holding whether or not gridlines are desired.

    """
    if plot_method == "from data array":
        plt.plot(cube.data)
    else:
        qplt.plot(cube)

    plt.gca().grid(gridlines)


def plot_2d(cube, plot_method, plot_type, projection, central_longitude, cmap,
            num_contours, cartographic, gridlines, contour_labels,
            colorbar_range, axes_labels):
    """
    Manages the plotting of 2D cubes

    Args:

    * cube
        The 2D cube to be plotted.

    * plot_method
        String holding the users choice of plotting using either quickplot or
        simply plotting from the data array.

    * plot_type
        String holding the type of plot to be used. Choose from pcolormesh,
        Contour and Contourf.

    * projection
        String holding the projection to be used for the plot. Can be any of
        the projections usable in Cartopy, or Automatic.

    * central_longitude
        Double representing the longitude to be positioined in the centre of
        the plot.

    * cmap
        String representing the colormap to be used. Can be any of the Brewer
        Colormaps supported by Iris, or Automatic.

    * num_contour
        int holding the number of contours to be plotted.

    * cartographic
        Dictionary containing Booleans for displaying coastlines, countries and
        rivers.

    * gridlines
        Boolean holding whether or not gridlines are desired.

    * contour_labels
        Boolean representing whether the contours on a Contour plot (not
        contourf) should be labeled.

    * colorbar_range
        Dictionary containing ints representing the max and min to which the
        colorbar will be set.

    * axes_labels
        list holding the names of the x and y coordinates.

    """
    if plot_method == "from data array":
        set_plot_data(cube, plot_type, cmap, num_contours, contour_labels,
                      colorbar_range, gridlines, axes_labels)

    else:
        set_projection(projection, central_longitude)
        set_plot(cube, plot_type, cmap, num_contours, contour_labels,
                 colorbar_range)
        try:
            set_cartographic(cartographic)
        except AttributeError:
            pass
        set_gridlines(gridlines)


def set_plot(cube, plot_type, cmap, num_contours, contour_labels,
             colorbar_range):
    """
    Produces a plot object for the desired cube using quickplot.

    Args:

    * cube
        The cube to be plotted.

    * plot_type
        String holding the type of plot to be used. Choose from pcolormesh,
        Contour and Contourf.

    * cmap
        String representing the colormap to be used. Can be any of the
        Brewer Colormaps supported by Iris, or Automatic.

    * num_contour
        int holding the number of contours to be plotted.

    * contour_labels
        Boolean representing whether the contours on a Contour plot
        (not contourf) should be labeled.

    * colorbar_range
        Dictionary containing ints representing the max and min to
        which the colorbar will be set.

    """
    # We unpack the colorbar_range dictionary
    colorbar_max = colorbar_range['max']
    colorbar_min = colorbar_range['min']
    # We obtain the levels used to define the contours.
    levels = get_levels(cube, colorbar_max, colorbar_min, num_contours)

    if plot_type == "Filled Contour":
        qplt.contourf(cube, num_contours, cmap=get_colormap(cmap),
                      levels=levels, vmax=colorbar_max, vmin=colorbar_min)
    elif plot_type == "Contour":
        contours = qplt.contour(cube, num_contours, cmap=get_colormap(cmap),
                                levels=levels, vmax=colorbar_max,
                                vmin=colorbar_min)
        if contour_labels:
            plt.clabel(contours, inline=1, fontsize=8)
    else:
        qplt.pcolormesh(cube, cmap=get_colormap(cmap), vmax=colorbar_max,
                        vmin=colorbar_min)


def set_plot_data(cube, plot_type, cmap, num_contours, contour_labels,
                  colorbar_range, gridlines, axis_labels):
    """
    Produces a plot object for the desired cube using matplotlib.pyplot methods

    Args:

    * cube
        The cube to be plotted.

    * plot_type
        String holding the type of plot to be used. Choose from
        pcolormesh, Contour and Contourf.

    * cmap
        String representing the colormap to be used. Can be any of the Brewer
        Colormaps supported by Iris, or Automatic.

    * num_contour
        int holding the number of contours to be plotted.

    * contour_labels
        Boolean representing whether the contours on a Contour plot (not
        contourf) should be labeled.

    * colorbar_range
        Dictionary containing ints representing the max and min to
        which the colorbar will be set.

    * axes_labels
        list holding the names of the x and y coordinates.

    """
    # We unpack the colorbar_range dictionary
    colorbar_max = colorbar_range['max']
    colorbar_min = colorbar_range['min']
    levels = get_levels(cube, colorbar_max, colorbar_min, num_contours)

    if plot_type == "Filled Contour":
        im = plt.contourf(cube.data, num_contours, cmap=get_colormap(cmap),
                          levels=levels, vmax=colorbar_max, vmin=colorbar_min)
        # We add a colorbar to the plot.
        plt.colorbar(im)
    elif plot_type == "Contour":
        contours = plt.contour(cube.data, num_contours,
                               cmap=get_colormap(cmap), levels=levels,
                               vmax=colorbar_max, vmin=colorbar_min)
        if contour_labels:
            plt.clabel(contours, inline=1, fontsize=8)
    else:
        im = plt.pcolormesh(cube.data, cmap=get_colormap(cmap),
                            vmax=colorbar_max, vmin=colorbar_min)
        plt.colorbar(im)

    if gridlines:
        plt.gca().grid(gridlines)

    # We ensure that the coord names correspond to the correct axis
    xlabel, ylabel = sort_axis_labels(cube, axis_labels)

    # Label the axes
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)


def set_projection(projection, central_longitude):
    """
    This function sets the projection to be used in the plot.

    Args:

    * projection
        String holding the projection to be used for the plot. Can be any of
        the projections usable in Cartopy, or Automatic.

    * central_longitude
        Double representing the longitude to be positioined in the centre of
        the plot.

    """
    if projection == "Automatic":
        # If there is no selected projection, then we do not specify anything,
        # and the natural projection of the data is used.
        pass
    else:
        # Ensure that the projection is written as needed for use with Cartopy.
        projection = projection.replace(" ", "")
        # Get the projection object
        get_projection = getattr(ccrs, projection)
        # The following projections do not have a central longitude argument.
        no_central_long_arg = ['OSGB', 'OSNI', 'EuroPP', 'Gnomonic',
                               'RotatedPole', 'Automatic']
        if projection in no_central_long_arg:
            plt.axes(projection=get_projection())
        else:
            plt.axes(projection=get_projection(
                     central_longitude=central_longitude))


def set_cartographic(cartographic):
    """
    Adds coastlines, country borders and rivers to the plot as desired.

    Args:

    * cartographic
        dictionary containing Booleans for displaying coastlines, countries and
        rivers.

    """
    # We unpack the cartographic dictionary
    coastlines = cartographic['coastlines']
    countries = cartographic['countries']
    rivers = cartographic['rivers']

    if coastlines:
        plt.gca().coastlines()

    if countries:
        countries = cfeature.NaturalEarthFeature(category='cultural',
                                                 name='admin_0_countries',
                                                 scale='50m',
                                                 facecolor='none')
        plt.gca().add_feature(countries)

    if rivers:
        plt.gca().add_feature(feature.RIVERS)
        plt.gca().add_feature(feature.LAKES)


def set_gridlines(gridlines):
    """
    Adds gridlines to the plot as desired

    Args:

    * gridlines
        Boolean holding whether or not gridlines are desired.

    Note:
        Different methods of adding gridlines exist...

        Quickplot does not add axis labels for lat/lon graphs.
        Therefore by preference, we attempt to draw gridlines with labels.
        This is done by using cartopy with the
        plt.gca().gridlines(draw_labels=True) method. This method will also
        be able to draw the correct gridlines on all projections.

        However, currently, this method will only work if the the graph is
        lat/long, and the labels will only function for a very limited number
        of projections.

        If the projection is not one which supports the labels, then a
        TypeError is returned. In this case, we can catch the error, and allow
        it to plot the gridlines without the labels.

        If the plot is not lat/lon, (or not created using quickplot) then the
        axes will not have this property at all, and so an Attribute error will
        be thrown. In this case, we must resort to the standard matplotlib
        method for adding gridlines.

    """
    if gridlines:
        try:
            grid = plt.gca().gridlines(draw_labels=True)
            grid.xlabels_top = False
        except AttributeError:
            plt.gca().grid(True)
        except TypeError:
            plt.gca().gridlines(draw_labels=False)


def get_colormap(cmap):
    """
    This method takes in the string that was given by the combobox, and returns
    the colormap in a form that can be entered as an argument for quickplot.

    Args:

    * cmap
        String containing the user's choice of cmap

    * colormap
        Returns a String or None containing the colormap to be used.

    """
    colormap = None if cmap == "Automatic" else cmap
    return colormap


def set_fixed_colorbar(cube, dim_indices, collapsed_indices):
    """
    This method finds the maximum and minimum values of the cube cube for
    all slices along a given dimension.

    Runs through all slices along the sliced dimension
    For each slice it takes the maximum and minimum value in the data.

    It then scans through and selects the maximum maximum and the
    minimum minimum, and returns these.

    Args:

    * cube
        The full cube, before it has been reduced.

    * dim_indices
        dictionary containing the index of the coordinates within the cube for
        the axes dimensions and the sliced dimension. For example, if the cube
        has coords time, lat and lon, then time would have index 0, lat 1 and
        lon 2.

     * collapsed_indices
        Same as dim_indices, except holding the indecies for all coordinates
        that are not aready accounted for.

    Returns:

    * max_cont, min_cont
        Doubles representing the maximum and minimum values of the data across
        all of the slices.

    """
    if cube.ndim > 2:

        sub_cube = get_sub_cube(cube, dim_indices, collapsed_indices)

        slice_max = []
        slice_min = []
        sliced_dim_index = dim_indices['sliced dim index']

        for slice_index in xrange(cube.shape[sliced_dim_index]):
            new_index = get_correct_index(dim_indices)
            cube_slice = extract_cube(sub_cube, [new_index], [slice_index])
            try:
                data_max, data_min = find_max_min(cube_slice)
                slice_max.append(data_max)
                slice_min.append(data_min)
            except ValueError:
                pass
        try:
            max_cont = np.nanmax(slice_max)
            min_cont = np.nanmin(slice_min)
        except ValueError:
            max_cont = None
            min_cont = None

    else:
        max_cont = None
        min_cont = None

    return max_cont, min_cont


def find_max_min(cube):
    """
    Returns the maximum and minimum values of a given cube.

    Args:

    * cube
        The cube for which the max and min are desired.

    Returns:

    * data_max, data_min
        Doubles representing the maximum and minimum values of data contained
        within the cube.

    """
    values = np.ma.array(cube.data)
    data = values.compressed()
    data_max = np.nanmax(data)
    data_min = np.nanmin(data)

    return data_max, data_min


def get_levels(cube, colorbar_max, colorbar_min, num_contours):
    """
    This function determines the positions of the levels used in the contour(f)
    methods. These levels specify the values for which the contours are drawn,
    and hence specify how the colorbar is set across the data. This function
    will return evenly spaced levels, but does allow for the total range to be
    either larger or smaller than the range of the values of the data.

    Args:

    * cube
        The cube to be plotted

    * colorbar_max, colorbar min
        Doubles representing the desired range oveR which the colorbar will be
        set. ie. red would be set to be shown at a value of colorbar max, and
        blue at a value of colorbar min.

    * num_contour
        int holding the number of contours to be plotted.

    Returns:

    * levels
        List of evenly spaced doubles, representing the positions at which the
        contours will be drawn.

    Note:
        Using the vmax/vmin arguments sets no. of contours across the range of
        values in the data sets range of colours in the specified range.
        ie... if temp data ranges from 295 - 300, and vmin/vmax 200 - 300,
        will plot 25 shades of red.... which i like.
        but.. if temp data ranges from 200 - 300, and vmin/vmax 250 - 255,
        it will plot blue across 12 contours, red across 12 and 1 green.
        This is unhelpful as it gives no extra detail on the specified range.

        A second method is to specify the levels to be used for each color
        boundary. This sets no. of contours across the specified range
        and sets the range of colours in the specified range.
        This ensures that in the situation where the range of vmin/vmax is
        smaller than the range of data, the full number of contours is utilised
        over the smaller range, giving better detail in the specified region.

        conclusion: vmax/vmin much better for when the range of the data is
        smaller than colorbar range levels much better for when the range
        of the data is larger than the colorbar range

        we therefore only set levels when data range > colorbar range.

    """
    if colorbar_max is None:
        levels = None
    else:
        data_max = np.max(cube.data)
        data_min = np.min(cube.data)
        max_level = colorbar_max if (data_max > colorbar_max) else data_max
        min_level = data_min if (data_min > colorbar_min) else colorbar_min

        seperation = (max_level - min_level) / (num_contours + 1)
        levels = []
        for i in range(num_contours + 2):
            next_level = min_level + (seperation * i)
            levels.append(next_level)
    return levels


def get_correct_index(dim_indices):
    """
    This function ensures that the index of the coordinate for the original
    cube is mapped to the correct coordinate of the smaller 3D cube. It
    returns the correct index for the sliced coordinate.

    Args:

    * dim_indices
        dictionary containing the index of the coordinates within the cube for
        the axes dimensions and the sliced dimension. For example, if the cube
        has coords time, lat and lon, then time would have index 0, lat 1 and
        lon 2.

    Returns:

    * new_index
        Double representing the correct index of the sliced coordinate in the
        new sub_cube.

    """
    dim_1_index = dim_indices['dim 1 index']
    dim_2_index = dim_indices['dim 2 index']
    sliced_dim_index = dim_indices['sliced dim index']

    new_index = 0
    if sliced_dim_index > dim_1_index or sliced_dim_index > dim_2_index:
        new_index = 1
    if sliced_dim_index > dim_1_index and sliced_dim_index > dim_2_index:
        new_index = 2

    return new_index


def check_extent(plot_method, can_draw_map):
    """
    This function is a workaround for a bug in cartopy present at the time
    of writing in which the transformation of the data leads to the extent
    of the data being far larger than the extent of the projection. This
    caused the graph to be zoomed way out, often to the point where the
    world was less than the size of a pixel.

    As a workaround, we compare the size of the extents from the data and the
    projection, and if we find that the data is larger, then we restrict the
    plot by calling set_global().

    We return a boolean describing if set_global has been called.

    Args:

    * plot_method
        String holding the users choice of plotting using either quickplot or
        simply plotting from the data array.

    * can_draw_map
        See iris.plot._can_draw_map(). This Boolean represents whether or not
        a plot is lat/long.

    Returns:

    * set_global
        Boolean representing whether or not the set global command has been
        called.

    """
    set_global = False
    if plot_method == "using quickplot" and can_draw_map:
        x_lims = np.fabs(plt.xlim())
        y_lims = np.fabs(plt.ylim())
        data_extent = (x_lims, y_lims)
        data_extent = np.reshape(data_extent, 4)

        x_lims = np.fabs(plt.gca().projection.x_limits)
        y_lims = np.fabs(plt.gca().projection.y_limits)
        projection_extent = (x_lims, y_lims)
        projection_extent = np.reshape(projection_extent, 4)

        difference = list(projection_extent - data_extent)

        if any(value < 0 for value in difference):
            plt.gca().set_global()
            set_global = True

    return set_global


def get_sub_cube(cube, dim_indices, collapsed_indices):
    """
    This function returns a 3 Dimensional cube, with the 3 remaining
    dimensions being the 2 chosen axes dimensions and the slice Dimension.

    The extraction itself is done by the extractCube function, so the
    main role of this method is to pass on the correct inputs for the
    extraction.

    Args:

    * dim_indices
        dictionary containing the index of the coordinates within the cube for
        the axes dimensions and the sliced dimension. For example, if the cube
        has coords time, lat and lon, then time would have index 0, lat 1 and
        lon 2.

     * collapsed_indices
        Same as dim_indices, except holding the indecies for all coordinates
        that are not aready accounted for.

    Results:

    * new_cube
        The collapsed 3D sub-cube.

    """
    dim_1_index = dim_indices['dim 1 index']
    dim_2_index = dim_indices['dim 2 index']
    sliced_dim_index = dim_indices['sliced dim index']
    coord_indices = []
    collapsed_dim_indices = []
    i = 0
    for dim_num in range(cube.ndim):
        if dim_num != dim_1_index and \
                dim_num != dim_2_index and \
                dim_num != sliced_dim_index:

            index = collapsed_indices[i]
            coord_indices.append(index)
            collapsed_dim_indices.append(dim_num)
            i += 1
    new_cube = extract_cube(cube, collapsed_dim_indices, coord_indices)

    return new_cube


def extract_cube(cube, dim_nums, coord_indices):
    """
    This function collapses the given cube using the method of cube indexing.
    It returns the collapsed cube.

    Args:

    * cube
        The cube to be collapsed.

    * dim_nums
        List of ints representing the index of the coordinates that will be
        collapsed.
        For example, if we have a 4D cube with coords, time, height, lat, lon,
        and we wanted to collapse it along height and lon, the the dim_nums
        would be [1,3]

    * coord_indices
        List of ints containing the indicies onto which the cube will be
        collapsed.
        Following on from the example above, if the height coordinate had
        points [110, 120, 130, 115] and lon had points [55, 57, 59], and we
        wanted to collase onto (130, 55), then the coord_indices would be
        [2,0].

    Returns:

    * new_cube
        The collapsed cube

    """
    slices = [slice(None)] * cube.ndim
    for index, dim_num in enumerate(dim_nums):
        slices[dim_num] = coord_indices[index]
    new_cube = cube[tuple(slices)]
    return new_cube


def sort_axis_labels(cube, axis_labels):
    """
    Takes in the axis labels, and arranges them so that they are sorted into
    the form xlabel, ylabel.

    Args:

    * cube
        The cube to which the labels belong. (The full cube before collapsing)

    *axis_labels
        List of Strings, representing the coordinate names of the x and y axes
        of the plot.

    """
    dim_names = get_dim_names(cube)
    sorted_list = []
    for name in dim_names:
        if name in axis_labels:
            sorted_list.append(name)
    if len(sorted_list) != 2:
        sorted_list = ('', '')
    return sorted_list[1], sorted_list[0]
