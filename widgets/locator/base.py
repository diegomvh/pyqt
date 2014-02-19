#!/usr/bin/env python

from PyQt4 import QtCore, QtGui

from .delegate import HtmlItemDelegate

class _CompleterModel(QtCore.QAbstractListModel):
    """QAbstractListModel implementation."""

    def __init__(self, parent = None):
        QtCore.QAbstractListModel.__init__(self, parent)
        self.completer = None
    
    def rowCount(self, index):
        """QAbstractItemModel method implementation"""
        if self.completer is None:
            return 0

        return self.completer.rowCount()
    
    def data(self, index, role):
        """QAbstractItemModel method implementation"""
        if self.completer is not None:
            if role == QtCore.Qt.DisplayRole:
                return self.completer.text(index.row(), index.column())
            elif role == QtCore.Qt.DecorationRole:
                return self.completer.icon(index.row(), index.column())
    
    def setCompleter(self, completer):
        """Set completer, which will be used as data source"""
        self.completer = completer
        self.modelReset.emit()

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
        
        # Input completer
        self._completer_model = _CompleterModel(self)
        self._completer = QtGui.QCompleter(self._completer_model, self)
        self._completer.setPopup(QtGui.QListView(self))
        self._completer.popup().setItemDelegate(
                        HtmlItemDelegate(self._completer.popup()))
        self._completer.setWidget(self._line_edit)
        
        self._line_edit.setFocus()
        
        
