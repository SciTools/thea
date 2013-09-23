SOURCES=about_dialog_layout.ui source_code_dialog_layout.ui colorbar_dialog_layout.ui main_window_layout.ui
PY_SOURCES=$(SOURCES:.ui=.py)

.PHONY: all clean

all: $(PY_SOURCES)

clean:
	rm -f $(PY_SOURCES) $(PY_SOURCES:.py=.pyc)

%.py: %.ui
	pyside-uic $< > $@
