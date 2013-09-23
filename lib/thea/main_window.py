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
This file contains the MainWindow Class.

"""
import matplotlib
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4'] = 'PySide'

import iris
import iris.plot as iplt
from matplotlib.backends.backend_qt4agg \
    import NavigationToolbar2QTAgg as NavigationToolbar
import matplotlib.pyplot as plt
from PySide import QtGui, QtCore
from PySide.QtGui import QApplication

import thea.about_dialog as about_dialog
import thea.colorbar_dialog as colorbar_dialog
import thea.cube_logic as cl
import thea.gui_logic as gl
from thea.main_window_layout import Ui_MainWindow
import thea.matplotlib_widget as matplotlib_widget
import thea.source_code_dialog as source_code_dialog
import thea.source_code_generator as source_code_generator
import thea.table_model as table_model



class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    """
    This class handles all of the direct interactions with the GUI itself. It
    is the class that creates the main window and manages dialog boxes, puts
    information into the objects within the window and reads the user input
    from these options.

    The majority of the caluculations, manipulations and plotting is found
    in other files.

    """
    def __init__(self, filename):
        """
        Initial setup of the window, including defining some instance
        variables, setting up the interface, and, if given, loading the
        first cube.

        Args:

        * filename
            String defining a path to a file or None.
            When called, the main window will either be called with a file to
            open imediately (cubeviz path) in which case the filename is the
            path, or without (cubeviz) in which the filename is None.

        """
        super(MainWindow, self).__init__()
        # define the dialogs to be used.
        self.colorbar_dialog = colorbar_dialog.ColorbarOptions()
        self.code_view = source_code_dialog.Viewer()
        self.about = about_dialog.About()

        # define some variables for this instance of the program

        # fixed_colorbar holds whether the calculation required to fix the
        # colorbar across all slices has been performed for this cube.
        self.filename = filename
        self.fixed_colorbar = False
        # colorbar_max/min define the range over which the colorbar is set.
        self.cube_loaded = False
        self.set_global = None
        self.can_draw_map = None
        # holds the number of dimensions of the current cube.
        self.ndim = 3
        # self.num_collapsed_dims ( = self.ndim - 3) holds the current no. of
        # collapsed dimension slots are required.
        self.num_collapsed_dims = 0
        self.init_ui()
        self.set_enabled()
        self.set_actions()
        if not filename is None:
            self.load_file(filename)
            self.set_dimension_combos()
            self.update()

    def init_ui(self):
        """
        This method sets up the initial layout of the GUI.

        """
        # First call the setupUi method created by Qt in theaMainInterface.
        self.setupUi(self)

        # creates a toolbar and addits it to the display widget.
        self.matplotlib_toolbar = NavigationToolbar(
            self.matplotlib_display.canvas, self.matplotlib_display)
        self.matplotlib_display.vbl.addWidget(self.matplotlib_toolbar)

        # creates a QTableView Object for the cube data.
        self.data_table = QtGui.QTableView(self.data_tab)
        self.data_table.setObjectName("dataTable")
        self.data_table.setAlternatingRowColors(True)
        self.gridLayout_8.addWidget(self.data_table, 0, 0, 1, 1)

        self.show()

    def set_actions(self):
        """
        This function sets up all of the interactivity for the GUI (except
        for that which was implemented directly in Qt Designer)

        Note:
            activated / triggered => when the user interacts with the object
            (ie. will not be sent if changed programatically)

            currentValueChanged and similar => when the object is changed
            either by the user or programatically

        """
        self.update_button.clicked.connect(self.update)

        # actions are the buttons placed on the main window toolbar.
        self.action_open.triggered.connect(self.show_open_dialog)
        self.action_save.triggered.connect(self.show_save_dialog)
        self.action_colorbar.triggered.connect(self.show_colorbar_dialog)
        self.action_gridlines.triggered.connect(self.set_enabled)
        self.action_coastlines.triggered.connect(self.set_enabled)
        self.action_country_boundaries.triggered.connect(self.set_enabled)
        self.action_rivers_and_lakes.triggered.connect(self.set_enabled)
        self.action_contour_labels.triggered.connect(self.set_enabled)
        self.action_next_slice.triggered.connect(self.next_slice)
        self.action_previous_slice.triggered.connect(self.previous_slice)
        self.action_about.triggered.connect(self.open_about_dialog)
        self.action_source_code.triggered.connect(self.generate_source_code)

        # set up signals from plot menu.
        self.select_plot_method.activated.connect(self.set_enabled)
        self.select_plot_type.activated.connect(self.set_enabled)
        self.select_projection.currentIndexChanged.connect(self.set_enabled)
        self.select_central_longitude.valueChanged.connect(self.set_enabled)
        self.select_colormap.currentIndexChanged.connect(self.set_enabled)
        self.contour_slider.valueChanged.connect(self.set_enabled)

        # set up signals from cube options.
        self.select_cube.activated.connect(self.set_dimension_combos)
        self.select_cube.activated.connect(self.state_changed_fix_colorbar)
        self.select_dimension_1.currentIndexChanged.connect(self.set_enabled)
        self.select_dimension_2.currentIndexChanged.connect(self.set_enabled)
        self.select_sliced_dim.currentIndexChanged.connect(
            self.state_changed_fix_colorbar)
        self.select_slice_combo.currentIndexChanged.connect(self.set_enabled)

        self.select_dimension_1.activated.connect(self.arrange_coords_1)
        self.select_dimension_2.activated.connect(self.arrange_coords_2)
        self.select_sliced_dim.activated.connect(self.arrange_coords_3)

        # signals from the colorbar_dialog window.
        self.colorbar_dialog.autoselect_range.stateChanged.connect(
            self.set_enabled)
        self.colorbar_dialog.fixed_colorbar.clicked.connect(
            self.state_changed_fix_colorbar)
        self.colorbar_dialog.min_contour.valueChanged.connect(
            self.set_enabled)
        self.colorbar_dialog.max_contour.valueChanged.connect(
            self.set_enabled)
        self.colorbar_dialog.autoselect_range.stateChanged.connect(
            self.update_max_min)
        self.colorbar_dialog.fixed_colorbar.clicked.connect(
            self.update_max_min)
        self.colorbar_dialog.manual_range.clicked.connect(self.update_max_min)

        self.cube_info_tab.currentChanged.connect(self.show_data)

    def set_dimension_combos(self):
        """
        This method is responisble for ensuring that all of the revelant
        combo boxes are filled with the correct coordinate names. It is
        called whenever the cube is changed.

        """
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        self.clear_dims()

        # Cube is set and the summary is printed to the information tab.
        self.cube = self.get_current_cube()
        self.print_cube_browser.setText(str(self.cube))

        # we check to see if we need to add or remove collapsed dim slots
        old_ndim = self.ndim if self.ndim > 3 else 3
        new_ndim = self.cube.ndim if self.cube.ndim > 3 else 3

        difference = new_ndim - old_ndim

        # adds more slots until there are enough.
        if difference > 0:
            for i in xrange(difference):
                self.num_collapsed_dims += 1
                self.add_collapsed_dim(self.num_collapsed_dims)

        # removes slots until there are the correct amount.
        if difference < 0:
            for _ in xrange(abs(difference)):
                self.remove_collapsed_dim(self.num_collapsed_dims)
                self.num_collapsed_dims -= 1

        # Set some instance variables about the cube.
        self.dim_names = gl.get_dim_names(self.cube)
        self.ndim = self.cube.ndim

        # Fill the combo boxes
        self.fill_combo("select_dimension_1", self.dim_names, True)

        if self.ndim >= 2:
            self.fill_combo("select_dimension_2", self.dim_names, True)

        if self.ndim >= 3:
            self.fill_combo("select_sliced_dim", self.dim_names, True)

            # get data on the coord points, and fill the combo box.
            dim = self.select_sliced_dim.currentText()
            data = gl.get_coord_values(self.cube, dim, self.dim_names)
            self.fill_combo("select_slice_combo", data, True)
            self.set_slice_scroll()
            self.select_slice_scroll.setEnabled(True)
            self.action_next_slice.setEnabled(True)
            self.action_previous_slice.setEnabled(True)

        self.set_initial_index()
        self.set_collapsed_dims()

        # Collapsed dims refers to all dimensions above 3. these dimensions
        # are not the plotted dimensions, nor are they the dimension in which
        # slices are to be taken... They are simply collapsed as chosen by the
        # user.

        self.set_enabled()

        # These placeholder variables keep a record of the current state of
        # the selectCoordinate combo boxes.
        self.dim_1 = self.select_dimension_1.currentIndex()
        self.dim_2 = self.select_dimension_2.currentIndex()
        self.dim_3 = self.select_sliced_dim.currentIndex()

        QApplication.restoreOverrideCursor()

    def update(self):
        """
        This method is called whenever a new cube is loaded, or when the
        update button is pressed. It is responsible for gathering the
        information needed to plot the cube from the interface, and passing
        it to the update function in cubeLogic. It also calls for the
        information about the sub cube to be displayed.

        """
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        self.update_button.setEnabled(False)

        interface_status = self.get_status()

        self.clear_fig()
        self.statusBar().showMessage('Drawing Cube')

        try:
            # passes information to the plotting function.
            self.plotted_cube, self.set_global = cl.update(interface_status)

        # Should anything fail during the plotting that was not explicitly
        # caught, the program produces dialog box containg the error message.
        except Exception as e:
            flags = QtGui.QMessageBox.StandardButton.Ok
            QtGui.QMessageBox.critical(
                self, 'Unable to plot cube!', str(e), flags)
            self.statusBar().showMessage('Failed to Plot Cube')
            QApplication.restoreOverrideCursor()

        # update the display and use the data from the plotted cube to print a
        # summary of the cube and show its data.
        self.display()
        self.print_cube_slice_browser.setText(str(self.plotted_cube))
        self.show_data()
        self.statusBar().showMessage('Ready')
        QApplication.restoreOverrideCursor()

    def show_open_dialog(self):
        """
        Handles the loading of a file, and calls functions to
        set up the GUI accordingly and then display the cube
        public samlpe data is used as default folder for now. Want to change
        this to default to the last folder that the program was in.

        """
        self.filename, _ = QtGui.QFileDialog.getOpenFileName(self, 'Open File')

        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.statusBar().showMessage('Loading Cube')

        self.load_file(self.filename)

        QApplication.restoreOverrideCursor()

        self.set_dimension_combos()
        self.update()

    def open_about_dialog(self):
        """
        Opens the about dialog box.

        """
        self.about.show()

    def show_save_dialog(self):
        """
        Opens a dialog box allowing you to save the current image.

        """
        filename, _ = QtGui.QFileDialog.getSaveFileName()

        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.statusBar().showMessage('Saving')

        try:
            plt.savefig(filename)
        except Exception as e:
            flags = QtGui.QMessageBox.StandardButton.Ok
            QtGui.QMessageBox.critical(
                self, 'Unable to Save Cube', str(e), flags)
            self.statusBar().showMessage('Save Failed')

        QApplication.restoreOverrideCursor()
        self.statusBar().showMessage('Ready')

    def get_current_cube(self):
        """
        Fetches the current cube from the list of loaded cubes.

        """
        cube_index = self.select_cube.currentIndex()
        return self.cubes[cube_index]

    def show_colorbar_dialog(self):
        """
        Brings up a new window containg options about the colorbar range.

        """
        self.colorbar_dialog.show()
        self.update_max_min()

    def state_changed_fix_colorbar(self):
        """
        Called whenever a fixed colorbar would need to be recalculated.

        """
        self.set_enabled()
        self.fixed_colorbar = False

    def update_max_min(self):
        """
        Updates the max and min boxes in colorbar dialog.

        There should be code in here which stops this process on large cubes...
        The time taken in this case is too large for the small reward.

        """
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        scheme = self.colorbar_dialog.get_colorbar_scheme()

        if scheme is "auto":
            colorbar_max, colorbar_min = cl.find_max_min(self.plotted_cube)
            self.colorbar_dialog.set_max_min(colorbar_max, colorbar_min)

        elif scheme is "fixed":
            # want to fix the colorbar across all of the slices.
            cube = self.cube
            dim_1_index = self.select_dimension_1.currentIndex()
            dim_2_index = self.select_dimension_2.currentIndex()
            sliced_dim_index = self.select_sliced_dim.currentIndex()
            dim_indices = {'dim 1 index': dim_1_index,
                           'dim 2 index': dim_2_index,
                           'sliced dim index': sliced_dim_index}
            collapsed_indices = []
            for i in xrange(self.ndim - 3):
                box_name = "select_slice_index_" + str(i+1)
                box = self.findChild(QtGui.QComboBox, box_name)
                collapsed_indices.append(box.currentIndex())

            colorbar_max, colorbar_min = cl.set_fixed_colorbar(
                cube, dim_indices, collapsed_indices)
            self.colorbar_dialog.set_max_min(colorbar_max, colorbar_min)

        QApplication.restoreOverrideCursor()

    def set_initial_index(self):
        """
        Sets the initial index of the select_dimension combo boxes.

        """
        if self.ndim == 1:
            self.select_dimension_1.setCurrentIndex(0)
        else:
            self.select_dimension_1.setCurrentIndex(self.ndim - 2)
            self.select_dimension_2.setCurrentIndex(self.ndim - 1)
            if self.ndim > 2:
                self.select_sliced_dim.setCurrentIndex(0)

    def clear_all(self):
        """
        Clears all information from the interface.

        """
        self.clear_dims()
        self.clear_fig()
        self.select_cube.clear()
        self.action_next_slice.setEnabled(False)
        self.action_previous_slice.setEnabled(False)

    def clear_dims(self):
        """
        Clears all information from the select Dimension combo boxes.

        """
        self.select_dimension_1.clear()
        self.select_dimension_2.clear()
        self.select_sliced_dim.clear()
        self.select_slice_combo.clear()

        self.select_dimension_1.setEnabled(False)
        self.select_dimension_2.setEnabled(False)
        self.select_sliced_dim.setEnabled(False)
        self.select_slice_combo.setEnabled(False)
        self.select_slice_scroll.setEnabled(False)
        self.action_load_slices.setEnabled(False)
        self.action_next_slice.setEnabled(False)
        self.action_previous_slice.setEnabled(False)

        self.fixed_colorbar = False

        self.clear_collapsed_dims()

    def clear_fig(self):
        """
        Clears the embedded figure to leave a blank canvas.

        """
        plt.clf()
        self.display()

    def clear_collapsed_dims(self):
        """
        Clears all information in the collapsed dims.
        Does not remove the boxes or labels... just clears them.

        """
        for i in xrange(self.ndim - 3):
            label_name = "collapsed_dim_" + str(i + 1)
            box_name = "select_slice_index_" + str(i + 1)
            label = self.findChild(QtGui.QLabel, label_name)
            box = self.findChild(QtGui.QComboBox, box_name)
            label.clear()
            box.clear()

    def next_slice(self):
        """
        Moves one step along the sliced dimension.

        """
        i = self.select_slice_combo.currentIndex()
        self.select_slice_combo.setCurrentIndex(i+1)
        self.update()

    def previous_slice(self):
        """
        Moves back one step in the sliced dimension.

        """
        i = self.select_slice_combo.currentIndex()
        if i == 0:
            i = self.select_slice_combo.count()
        self.select_slice_combo.setCurrentIndex(i-1)
        self.update()

    def arrange_coords_1(self):
        """
        The arrange Methods are present to prevent any one coordinate
        being used more than once in the selectDimension1,
        selectDimension2 and selectSlicedDim combo boxes.

        When a coordinate is selected in any one of the combo boxes,
        it checks the other 2 for matches and if matches are found
        then it will put the old value for the selected combo box into
        the combo box with the match.

        """
        dim_1_name = self.select_dimension_1.currentText()
        dim_2_name = self.select_dimension_2.currentText()
        sliced_dim_name = self.select_sliced_dim.currentText()

        if dim_1_name == dim_2_name:
            self.select_dimension_2.setCurrentIndex(self.dim_1)
        elif dim_1_name == sliced_dim_name:
            self.select_sliced_dim.setCurrentIndex(self.dim_1)
        self.dim_1 = self.select_dimension_1.currentIndex()
        self.dim_2 = self.select_dimension_2.currentIndex()
        self.dim_3 = self.select_sliced_dim.currentIndex()

        if self.ndim > 2:
            dim = self.select_sliced_dim.currentText()
            data = gl.get_coord_values(self.cube, dim, self.dim_names)
            self.fill_combo("select_slice_combo", data, True)
            self.set_slice_scroll()
            self.set_collapsed_dims()

    def arrange_coords_2(self):
        """
        Same as arrange coords 1 except that this is for when select
        dimension 2 is changed.

        """
        dim_1_name = self.select_dimension_1.currentText()
        dim_2_name = self.select_dimension_2.currentText()
        sliced_dim_name = self.select_sliced_dim.currentText()

        if dim_2_name == dim_1_name:
            self.select_dimension_1.setCurrentIndex(self.dim_2)
        elif dim_2_name == sliced_dim_name:
            self.select_sliced_dim.setCurrentIndex(self.dim_2)

        self.dim_1 = self.select_dimension_1.currentIndex()
        self.dim_2 = self.select_dimension_2.currentIndex()
        self.dim_3 = self.select_sliced_dim.currentIndex()

        if self.ndim > 2:
            dim = self.select_sliced_dim.currentText()
            data = gl.get_coord_values(self.cube, dim, self.dim_names)
            self.fill_combo("select_slice_combo", data, True)
            self.set_slice_scroll()
            self.set_collapsed_dims()

    def arrange_coords_3(self):
        """
        Same as arrange coord 1 except that this is for when select_sliced_dim
        is pressed.

        """
        dim_1_name = self.select_dimension_1.currentText()
        dim_2_name = self.select_dimension_2.currentText()
        sliced_dim_name = self.select_sliced_dim.currentText()

        if sliced_dim_name == dim_1_name:
            self.select_dimension_1.setCurrentIndex(self.dim_3)
        elif sliced_dim_name == dim_2_name:
            self.select_dimension_2.setCurrentIndex(self.dim_3)
        self.dim_1 = self.select_dimension_1.currentIndex()
        self.dim_2 = self.select_dimension_2.currentIndex()
        self.dim_3 = self.select_sliced_dim.currentIndex()

        if self.ndim > 2:
            dim = self.select_sliced_dim.currentText()
            data = gl.get_coord_values(self.cube, dim, self.dim_names)
            self.fill_combo("select_slice_combo", data, True)
            self.set_slice_scroll()
            self.set_collapsed_dims()

    def set_collapsed_dims(self):
        """
        Beyond 3 dimensions, the program allows you to pick a single value
        to collapse the cube around. This method fills and enables the
        relevant labels and combo boxes to allow this.

        """
        if self.ndim > 3:
            used_dims = []
            used_dims.append(self.select_dimension_1.currentText())
            used_dims.append(self.select_dimension_2.currentText())
            used_dims.append(self.select_sliced_dim.currentText())
            unused_dims = gl.get_remaining_dims(self.dim_names, used_dims)

            for i in xrange(len(unused_dims)):
                label_name = "collapsed_dim_" + str(i+1)
                box_name = "select_slice_index_" + str(i+1)

                label = self.findChild(QtGui.QLabel, label_name)
                label.setText(unused_dims[i])

                data = gl.get_coord_values(self.cube, unused_dims[i],
                                           self.dim_names)
                self.fill_combo(box_name, data, True)

    def add_collapsed_dim(self, num):
        """
        Adds a new collased dim slot.

        For cubes which have more than 3 dimensions, we add and remove extra
        buttons and labels dynamically. These are named collapsed dim slots.

        This method creates a new slot by adding a new label and comboBox.

        Args:

        * num
            int. Hold the number of collapsed dims that will be present after
            adding this one.

        """
        if num == 1:
            label_name = "collapsed_dims"
            label = QtGui.QLabel(self.dim_options_frame)
            label.setText('Collapsed Dims:')
            self.gridLayout_9.addWidget(label, (11), 0, 1, 2)
            label.setObjectName(label_name)

        label_name = "collapsed_dim_" + str(num)
        box_name = "select_slice_index_" + str(num)

        label = QtGui.QLabel(self.dim_options_frame)
        box = QtGui.QComboBox(self.dim_options_frame)

        self.gridLayout_9.addWidget(label, (11 + num), 0, 1, 1)
        self.gridLayout_9.addWidget(box, (11 + num), 1, 1, 1)

        label.setObjectName(label_name)
        box.setObjectName(box_name)

        box.activated.connect(self.set_enabled)

    def remove_collapsed_dim(self, num):
        """
        Removes the latest collapsed dim slot.

        For cubes which have more than 3 dimensions, we add and remove extra
        buttons and labels dynamically. These are named collapsed dim slots.

        This method creates a new slot by removing the newest label and
        comboBox.

        Args:

        * num
            int. Holds the number of collapsed dim slots there are before
            removing this one.

        """
        if num == 1:
            label_name = "collapsed_dims"
            label = self.findChild(QtGui.QLabel, label_name)
            label.deleteLater()
        # Revomes the most recent collapsed dim slot.
        label_name = "collapsed_dim_" + str(num)
        box_name = "select_slice_index_" + str(num)

        label = self.findChild(QtGui.QLabel, label_name)
        box = self.findChild(QtGui.QComboBox, box_name)

        label.deleteLater()
        box.deleteLater()

    def set_slice_scroll(self):
        """
        Sets the correct number of steps there are in the scrollbar of the
        current coordinate

        """
        sliced_coord = self.select_sliced_dim.currentText()
        data = gl.get_coord_values(self.cube, sliced_coord, self.dim_names)
        max_slice = len(data)
        self.select_slice_scroll.setMaximum(max_slice - 1)

    def fill_combo(self, box_name, data, enabled):
        """
        We add all of the items in data, to the specified combo box.

        Args:

        * box_name
            String containing the name of the comboBox that you want to add
            data too.

        * data
            list containing the data that you would like to add to the box.

        * enabled
            Boolean containing if the box should be enabled or disabled
            initially

        """
        combo_box = self.findChild(QtGui.QComboBox, box_name)
        combo_box.clear()
        if enabled:
            combo_box.setEnabled(True)
            for item in data:
                combo_box.addItem(str(item))
        else:
            combo_box.setEnabled(False)

    def show_data(self):
        """
        Here we take the currently plotted cube (in general NOT the full
        cube) and write the data in it into a table.

        """
        if self.cube_info_tab.currentIndex() == 2:
            QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            self.data_table.clearSpans()

            if self.ndim == 1:
                coord_1 = None
                coord_2 = self.select_dimension_1.currentText()
                horiz_headers = [""]

            else:
                dim_1 = self.select_dimension_1.currentIndex()
                dim_2 = self.select_dimension_2.currentIndex()
                if dim_1 < dim_2:
                    coord_1 = self.select_dimension_1.currentText()
                    coord_2 = self.select_dimension_2.currentText()
                else:
                    coord_1 = self.select_dimension_2.currentText()
                    coord_2 = self.select_dimension_1.currentText()
                try:
                    horiz_headers = self.cube.coord(coord_2).points
                # An anonymous coord will not be found.
                except iris.exceptions.CoordinateNotFoundError:
                    # We default to using the index.
                    horiz_headers = [i for i in xrange(
                        self.plotted_cube.shape[1])]

            data = self.plotted_cube.data.tolist()
            try:
                vert_headers = self.cube.coord(coord_1).points
            except iris.exceptions.CoordinateNotFoundError:
                vert_headers = [i for i in xrange(self.plotted_cube.shape[0])]

            table = table_model.TableModel(data, horiz_headers,
                                           vert_headers, self.data_tab)
            self.data_table.setModel(table)
            QApplication.restoreOverrideCursor()

    def generate_source_code(self):
        """
        collects information from the GUI, and then calls function to
        create source code for the image. Finally, it passes the source code to
        a new window to be viewed.

        """
        status = self.get_status()

        coord_indices = []
        counter = 1
        for dim in xrange(self.ndim):
            if dim == self.dim_1 or dim == self.dim_2:
                index = ":"
            elif dim == self.dim_3:
                index = self.select_slice_combo.currentIndex()
            else:
                box_name = "select_slice_index_" + str(counter)
                box = self.findChild(QtGui.QComboBox, box_name)
                index = box.currentIndex()
                counter += 1
            coord_indices.append(index)

        # We can now generate the code.
        code = source_code_generator.generate_code(status, coord_indices)
        # Pass the code to the code_view window and then open the window.
        self.code_view.set_code(code)
        self.code_view.show()

    def set_enabled(self):
        """
        This function controls which objects in the main window are enabled
        at any point. It is called whenever the user makes a change to the
        window.

        """
        status = self.get_status()

        state = gl.get_enabled(status)

        self.can_draw_map = state['cartographic']

        if self.can_draw_map is False:
            self.select_projection.setCurrentIndex(0)

        self.colorbar_dialog.disable_fixed_colorbar(self.ndim)

        self.action_previous_slice.setEnabled(state['previous'])
        self.action_next_slice.setEnabled(state['next'])
        self.action_source_code.setEnabled(state['source code'])
        self.action_coastlines.setEnabled(state['cartographic'])
        self.action_contour_labels.setEnabled(state['labels'])
        self.action_country_boundaries.setEnabled(state['cartographic'])
        self.action_rivers_and_lakes.setEnabled(state['cartographic'])
        self.action_colorbar.setEnabled(state['colorbar'])
        self.select_projection.setEnabled(state['cartographic'])
        self.select_central_longitude.setEnabled(state['central longitude'])
        self.select_plot_type.setEnabled(state['plot type'])
        self.select_colormap.setEnabled(state['colormap'])
        self.contour_slider.setEnabled(state['contour slider'])
        self.contour_label_frame.setEnabled(state['contour slider'])
        self.select_sliced_dim.setEnabled(state['third dim'])
        self.select_slice_combo.setEnabled(state['third dim'])
        self.select_slice_scroll.setEnabled(state['third dim'])
        self.update_button.setEnabled(state['update'])

    def get_status(self):
        """
        This method gathers information from around the interface, and then
        packages it up into a dictionary which can be neatly passed around.

        """
        cube_loaded = self.cube_loaded
        if cube_loaded:
            filename = self.filename
            cube_index = self.select_cube.currentIndex()
            set_global = self.set_global
            cube = self.get_current_cube()
            dim_1_index = self.select_dimension_1.currentIndex()
            dim_2_index = self.select_dimension_2.currentIndex()
            sliced_dim_index = self.select_sliced_dim.currentIndex()
            central_longitude = self.select_central_longitude.value()
            dim_indices = {'dim 1 index': dim_1_index,
                           'dim 2 index': dim_2_index,
                           'sliced dim index': sliced_dim_index}
            collapsed_indices = []
            for dim in xrange(cube.ndim - 3):
                box_name = "select_slice_index_" + str(dim+1)
                box = self.findChild(QtGui.QComboBox, box_name)
                collapsed_indices.append(box.currentIndex())
            can_draw_map = self.can_draw_map
            dim_1_name = self.select_dimension_1.currentText()
            dim_2_name = self.select_dimension_2.currentText()
            scheme = self.colorbar_dialog.get_colorbar_scheme()
            if scheme == "auto":
                self.colorbar_max = None
                self.colorbar_min = None
            elif scheme == "fixed":
                if not self.fixed_colorbar:
                    self.colorbar_max, self.colorbar_min = \
                        cl.set_fixed_colorbar(cube, dim_indices,
                                              collapsed_indices)
                    self.fixed_colorbar = True
            else:
                self.colorbar_max = self.colorbar_dialog.max_contour.value()
                self.colorbar_min = self.colorbar_dialog.min_contour.value()
            colorbar_range = {'max': self.colorbar_max,
                              'min': self.colorbar_min}
            slice_index = self.select_slice_scroll.value()
        else:
            filename = cube_index = set_global = cube = None
            dim_indices = collapsed_indices = can_draw_map = None
            dim_1_name = dim_2_name = colorbar_range = None
            slice_index = None
            central_longitude = None

        plot_method = self.select_plot_method.currentText()
        plot_type = self.select_plot_type.currentText()
        projection = self.select_projection.currentText()
        cmap = self.select_colormap.currentText()
        num_contours = self.contour_slider.value()
        coastlines = self.action_coastlines.isChecked()
        gridlines = self.action_gridlines.isChecked()
        contour_labels = self.action_contour_labels.isChecked()
        countries = self.action_country_boundaries.isChecked()
        rivers = self.action_rivers_and_lakes.isChecked()
        cartographic = {'coastlines': coastlines,
                        'countries': countries,
                        'rivers': rivers}

        interface_status = {'cube loaded': cube_loaded,
                            'cube': cube,
                            'plot method': plot_method,
                            'plot type': plot_type,
                            'projection': projection,
                            'central longitude': central_longitude,
                            'cmap': cmap,
                            'num contours': num_contours,
                            'cartographic': cartographic,
                            'gridlines': gridlines,
                            'contour labels': contour_labels,
                            'colorbar range': colorbar_range,
                            'dim indices': dim_indices,
                            'slice index': slice_index,
                            'collapsed indices': collapsed_indices,
                            'can draw map': can_draw_map,
                            'set global': set_global,
                            'filename': filename,
                            'cube index': cube_index,
                            'dim 1 name': dim_1_name,
                            'dim 2 name': dim_2_name}

        return interface_status

    def load_file(self, filename):
        """
        Loads a file into memory using the iris.load() method.
        Adds the names of the cube to the select cube combo_box.
        Sets cube_loaded to true.

        Args:

        * filename
            String containing the path to the file that should be opened.

        """
        try:
            self.cubes = iris.load(filename)
        except ValueError as e:
            flags = QtGui.QMessageBox.StandardButton.Ok
            QtGui.QMessageBox.critical(
                self, 'Unable to Load Cube: File type could not be read',
                str(e), flags)
            self.statusBar().showMessage('Load Failed')
            QApplication.restoreOverrideCursor()

        # Clear everything, to allow for objects to be rewritten for the
        # new cube.
        self.clear_all()

        # fill the select cube bow with the cube names in the cube list.
        # enable this box iff there is more than one cube to choose from.
        for self.cube in self.cubes:
            self.select_cube.addItem(self.cube.name())
        if len(self.cubes) == 1:
            self.select_cube.setEnabled(False)
        else:
            self.select_cube.setEnabled(True)

        self.cube_loaded = True

    def display(self):
        """
        Passes the current figure to the matplotlib display.

        """
        matplotlib_widget.fig = plt.gcf()
        self.matplotlib_display.canvas.draw()
