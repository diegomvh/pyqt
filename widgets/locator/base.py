#!/usr/bin/env python

from PyQt4 import QtCore, QtGui

class LocatorWidget(QtGui.QWidget):
    """Locator widget"""
    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        
        # Setup layout
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        
        # Create and setup main input widget
        self._line_edit = QtGui.QLineEdit(self)
        self.layout().addWidget(self._line_edit)
        self.setFocusProxy(self._line_edit)
        self._line_edit.setFocus()
