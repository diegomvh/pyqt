#!/usr/bin/env python

import re

from PyQt4 import QtCore, QtGui

from .completer import makeSuitableCompleter, RangeCompleter

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

import os

class OpenCommand(AbstractCommand):
    def signature(self):
        return "o <path> [line]"
    
    def description(self):
        return "Open file and go to line number"
    
    def pattern(self):
        return re.compile("o\s+([\w/\.-]*)\s*(\d*)")
    
    def completer(self, match, position):
        print(match.string, match.groups(), position)
        if match.span(1)[0] <= position <= match.span(1)[1]:
            return makeSuitableCompleter(match.groups()[0], position)
        if match.span(2)[0] <= position <= match.span(2)[1]:
            path = match.group(1)
            if os.path.isfile(path):
                return RangeCompleter(range(len(open(path).readlines())))

    def execute(self, match):
        print("testing")