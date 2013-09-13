Generated Files
===============

The .py files found in this directory are used in the program to create the
basic layout of the dialog box or window. They setup the initial size of the
window, the location of the objects within it, and the initial properties of
both the window and the objects within them.

These files were generated from a design of the window created using Qt
Designer. The .ui files found here are the files made by Qt Designer to
describe the interface that has been built. Each of the .ui files are therefore
a save of the design of the corresponding window.

If you wish to edit any of the dialogs/windows, then you have 2 options.

* You can edit the .py file directly. If you are familiar with PySide, then you
are able to read and change the python code directly.

* The recomended method is to open the .ui file in Qt Designer. You can now
use Qt Designer to edit the window. Once you are happy with this, save the file
again. To create the .py file, you will need to use pyside-uic as descirbed
below.

Converting .ui < .py
--------------------

Navigating to the directory containing pyside-uic, type the following into the
command line to convert your .ui file named source into a .py file named target.

```
pyside-uic source.ui > target.py
```


