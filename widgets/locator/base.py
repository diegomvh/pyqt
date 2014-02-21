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
        self._current_command = None
        self._current_inline = None
        
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
        
        self._completer.activated[QtCore.QModelIndex].connect(self._on_completer_activated)
        
        self._completer.setWidget(self._line_edit)
        
        self._line_edit.installEventFilter(self)
        self._line_edit.setFocus()

    # -------- Set and bind completer to completer modelReset
    def complete(self, completer):
        #Has inline
        self._current_inline = completer.inline()
        if self._current_inline:
            self._line_edit.blockSignals(True)
            position = self._line_edit.cursorPosition()
            self._line_edit.insert(self._current_inline)
            self._line_edit.setCursorPosition(position)
            self._line_edit.setSelection(position, len(self._current_inline))
            self._line_edit.blockSignals(False)

        self._completer_model.setCompleter(completer)
        self._completer.popup().verticalHeader().setVisible(completer.hasVerticalHeader())
        self._completer.popup().horizontalHeader().setVisible(completer.hasHorizontalHeader())
        self._completer.popup().resizeRowsToContents()
        self._completer.complete()
        if completer.hasHorizontalHeader():
            size = self._completer.popup().size()
            size.setHeight(size.height() + self._completer.popup().horizontalHeader().height())
            self._completer.popup().resize(size)

    # -------- Event filter
    def eventFilter(self, obj, event):
        # TODO Cuidado con esto que esta entrando por dos puntos
        if obj == self._line_edit and event.type() in (QtCore.QEvent.KeyPress, QtCore.QEvent.ShortcutOverride):
            if event.key() in (QtCore.Qt.Key_Tab, ) and self._current_inline is not None:
                self._line_edit.deselect()
                self._line_edit.setCursorPosition(self._line_edit.cursorPosition() + len(self._current_inline))
                self._line_edit.textChanged.emit(self._line_edit.text())
                return True
            elif event.key() in (QtCore.Qt.Key_Backspace, ) and self._current_inline is not None:
                self._line_edit.blockSignals(True)
                self._line_edit.insert("")
                self._line_edit.blockSignals(False)
        return QtGui.QWidget.eventFilter(self, obj, event)

    # -------- Signals
    def _on_completer_activated(self, index):
        print(index)
        
    def _on_line_edit_textChanged(self, text):
        current_completer = None
        self._current_command, match = self._parse_command(text)
        if self._current_command is not None:
            completer = self._current_command.completer(match, self._line_edit.cursorPosition())

            if completer is None:
                completer = _HelpCompleter([ self._current_command ])
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
