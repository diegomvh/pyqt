from PyQt4 import QtCore, QtGui

class AbstractCompleter(QtCore.QObject):
    def rowCount(self):
        """Row count for list"""
        raise NotImplemented()
    
    def text(self, row):
        """Text for list item"""
        raise NotImplemented()
    
    def icon(self, row):
        """Icon for list item. Default is None"""
        return None

class TestCompleter(AbstractCompleter):
    def __init__(self, parent = None):
        AbstractCompleter.__init__(self, parent)
        self.words = ["one", "two", "three", "four"]
    
    def rowCount(self):
        return len(self.words)
    
    def text(self, row):
        return self.words[row]
    
    def icon(self, row):
        return None
    