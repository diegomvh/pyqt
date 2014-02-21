#!/usr/bin/env python

from PyQt4 import QtCore, QtGui

from .delegate import HtmlItemDelegate, htmlEscape
from .completer import AbstractCompleter

class _CompleterModel(QtCore.QAbstractListModel):
    """QAbstractListModel implementation."""

    def __init__(self, parent = None):
        QtCore.QAbstractListModel.__init__(self, parent)
        self.completer = None
    
    def headerData(self, index, orientation, role):
        if self.completer is not None and role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.completer.horizontalHeader()
            else:
                return self.completer.verticalHeader(index)

    def rowCount(self, index):
        """QAbstractListModel method implementation"""
        if self.completer is None:
            return 0

        return self.completer.rowCount()
    
    def data(self, index, role):
        """QAbstractListModel method implementation"""
        if self.completer is not None:
            if role == QtCore.Qt.DisplayRole:
                return self.completer.display(index.row())
            elif role == QtCore.Qt.DecorationRole:
                return self.completer.decoration(index.row())
    
    def setCompleter(self, completer):
        """Set completer, which will be used as data source"""
        self.completer = completer
        self.modelReset.emit()

class _HelpCompleter(AbstractCompleter):
    def __init__(self, commands):
        self._commands = commands
        self._template = "<p><strong>%s</strong> (%s)</p>"
    
    def rowCount(self):
        return len(self._commands)
    
    def display(self, row):
        c = self._commands[row]
        return self._template % (
            htmlEscape(c.signature()),
            htmlEscape(c.description())
        )

class LocatorWidget(QtGui.QWidget):
    """Locator widget"""
    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        # Instance attrs
        self._commands = []
        
        # Setup layout
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        
        # Create and setup main input widget
        self._line_edit = QtGui.QLineEdit(self)
        self._line_edit.textChanged.connect(self._on_line_edit_textChanged)
        self.layout().addWidget(self._line_edit)
        self.setFocusProxy(self._line_edit)
        
        # Input completer
        self._completer_model = _CompleterModel(self)
        self._completer = QtGui.QCompleter(self._completer_model, self)
        self._completer.setPopup(QtGui.QTableView(self))
        self._completer.popup().setItemDelegate(
                        HtmlItemDelegate(self._completer.popup()))
        self._completer.popup().verticalHeader().setVisible(False)
        self._completer.popup().horizontalHeader().setVisible(False)
        self._completer.popup().horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
        self._completer.popup().setShowGrid(False)
        self._completer.popup().setAlternatingRowColors(True)
        self._completer.popup().setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._completer.popup().setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self._completer.popup().setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        
        # TODO ? Activated ?
        self._completer.popup().clicked.connect(self._on_popup_view_clicked)
        
        self._completer.setWidget(self._line_edit)
        
        self._line_edit.setFocus()

    # -------- Set and bind completer to completer modelReset
    def complete(self, completer):
        self._completer_model.setCompleter(completer)
        self._completer.popup().verticalHeader().setVisible(completer.hasVerticalHeader())
        self._completer.popup().horizontalHeader().setVisible(completer.hasHorizontalHeader())
        self._completer.popup().resizeRowsToContents()
        self._completer.complete()
        if completer.hasHorizontalHeader():
            size = self._completer.popup().size()
            size.setHeight(size.height() + self._completer.popup().horizontalHeader().height())
            self._completer.popup().resize(size)
        
        
    # -------- Signals
    def _on_popup_view_clicked(self, index):
        print(index)
        
    def _on_line_edit_textChanged(self, text):
        current_completer = None
        
        command, match = self._parse_command(text)
        if command is not None:
            completer = command.completer(match, self._line_edit.cursorPosition())

            if completer is None:
                completer = _HelpCompleter([ command ])
        else:
            completer = _HelpCompleter(self._commands)
    
        self.complete(completer)
    
    # -------- Command tools
    def _parse_command(self, text):
        """Parse text and try to get command"""
        for command in self._commands:
            match = command.pattern().match(text)
            if match:
                return command, match
        return None, None

    # -------- Command api
    def addCommand(self, command):
        self._commands.append(command)
    
    def removeCommand(self, command):
        self._commands.remove(command)
