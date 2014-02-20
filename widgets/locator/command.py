#!/usr/bin/env python

import re

from PyQt4 import QtCore, QtGui

from .completer import makeSuitableCompleter

class AbstractCommand(QtCore.QObject):
    def signature(self):
        raise NotImplemented()
    
    def description(self):
        raise NotImplemented()

    def pattern(self):
        raise NotImplemented()
    
    def completer(self, match, position):
        return None

    def execute(self, match):
        raise NotImplemented()

class TestCommand(AbstractCommand):
    def signature(self):
        return "t word"
    
    def description(self):
        return "Test Command"
    
    def pattern(self):
        return re.compile("t\s+(\w*)")
    
    def completer(self, match, position):
        print(match.groups())
        return makeSuitableCompleter(match.groups()[0], position)

    def execute(self, match):
        print("testing")