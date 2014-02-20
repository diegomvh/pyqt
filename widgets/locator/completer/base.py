from PyQt4 import QtCore, QtGui

class AbstractCompleter(QtCore.QObject):
    def rowCount(self):
        """Row count for list"""
        raise NotImplemented()
    
    def display(self, row):
        """Text for list item"""
        raise NotImplemented()
    
    def decoration(self, row):
        """Icon for list item. Default is None"""
        return None
    
    def hasHorizontalHeader(self):
        return False
    
    def hasVerticalHeader(self):
        return False
    
class WordsCompleter(AbstractCompleter):
    def __init__(self, words, parent = None):
        AbstractCompleter.__init__(self, parent)
        self.words = words
    
    def rowCount(self):
        return len(self.words)
    
    def display(self, row):
        return self.words[row]
    
    def decoration(self, row):
        return None
        
class RangeCompleter(AbstractCompleter):
    def __init__(self, numbers, parent = None):
        AbstractCompleter.__init__(self, parent)
        self.numbers = numbers

    def rowCount(self):
        return len(self.numbers)
    
    def display(self, row):
        return self.numbers[row]
    
    def decoration(self, row):
        return None
    