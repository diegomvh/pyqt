#!/usr/bin/env python

from PyQt4 import QtGui, QtCore
    
class HtmlItemDelegate(QtGui.QItemDelegate):
    def __init__(self, parentView):
        QtGui.QItemDelegate.__init__(self, parentView)
        self.document = QtGui.QTextDocument(self)
        self.document.setDocumentMargin(2)

    def drawDisplay(self, painter, option, rect, text):
        # Fix if not table
        text = "<table width='100%%'><tr><td>%s</td></tr></table>" % text
        
        if option.state & QtGui.QStyle.State_Selected:
            background = option.palette.color(QtGui.QPalette.Active, QtGui.QPalette.Highlight)
            color = option.palette.color(QtGui.QPalette.Active, QtGui.QPalette.HighlightedText)
            self.document.setDefaultStyleSheet("""table { background-color: %s;
                color: %s; }""" % (background.name(), color.name()))
        else:
            self.document.setDefaultStyleSheet("")

        self.document.setHtml(text)
        self.document.setTextWidth(option.rect.width() - option.decorationSize.width())
        
        ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()
        painter.save()
        
        painter.translate(QtCore.QPoint(rect.left(), option.rect.top()))
        dl = self.document.documentLayout()
        dl.draw(painter, ctx)
        painter.restore()

    def sizeHint(self, option, index):
        record = index.data()
        self.document.setHtml(record)
        self.document.setTextWidth(option.rect.width())
        return QtCore.QSize(self.document.idealWidth(), self.document.size().height())