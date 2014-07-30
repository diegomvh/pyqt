#!/usr/bin/env python

import collections

from PyQt4 import QtCore, QtGui

class Notification(QtGui.QLabel):
    
    margin = 10
    
    def __init__(self, content, links, timeout, parent):
        super(Notification, self).__init__(parent)
        
        self.links = links
        self.setText(content)
        self.adjustSize()
        
        self.linkActivated.connect(self.linkHandler)
        
        self.goe = QtGui.QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.goe)

        self.timeoutTimer = QtCore.QTimer(self)
        self.timeoutTimer.setSingleShot(True)
        self.setWindowOpacity(0.0)
        self.show()
        
        self.animationIn = QtCore.QPropertyAnimation(self.goe, "opacity")
        self.animationIn.setDuration(300)
        self.animationIn.setStartValue(0)
        self.animationIn.setEndValue(1.0)
        self.animationIn.finished.connect(self.timeoutTimer.start)

        self.animationOut = QtCore.QPropertyAnimation(self.goe, "opacity")
        self.animationOut.setDuration(300)
        self.animationOut.setStartValue(1.0)
        self.animationOut.setEndValue(0)
        self.animationOut.finished.connect(self.hide)

        self.timeoutTimer.timeout.connect(self.animationOut.start)
        self.timeoutTimer.setInterval(timeout)
        self.animationIn.start()
    
    def linkHandler(self, link):
        callback = self.links.get(link, None)
        if isinstance(callback, collections.Callable):
            callback()
  
    def updatePosition(self, point = None):
        if point is not None:
            x, y = point.x(), point.y()
        else:
            rect = self.parent().geometry()
            x = rect.width() - self.width() - self.margin
            y = rect.height() - self.height() - self.margin

        self.setGeometry(x, y, self.width(), self.height())

    def enterEvent(self, event):
        if self.timeoutTimer.isActive():
            self.timeoutTimer.stop()
    
    def leaveEvent(self, event):
        self.timeoutTimer.start()

class OverlayNotifier(QtGui.QWidget):
    def __init__(self, parent = None):
        super(OverlayNotifier, self).__init__(parent)
        parent.installEventFilter(self)
        self.notifications = []
        
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Resize:
            for key, notification, point in self.notifications:
                notification.updatePosition(point)
        return super(OverlayNotifier, self).eventFilter(obj, event)

    def showMessage(self, message, title="", frmt="text", timeout=2000, icon=None,
        point=None, links={}, key=None):
        if title:
            title = "%s:\n" % title if frmt == "text" else "<h4>%s</h4>" % title
        message = title + message
        if frmt == "text" and links:
            message = "<pre>%s</pre>" % message
        if links:
            message += "<div style='text-align: right; font-size: small;'>"
            for key in links.keys():
                message += "<a href='%s'>%s</a>" % (key, key.title())
            message += "</div>"

        notification = Notification(message, links, timeout, self.parent())
        notification.updatePosition(point)
        self.notifications.append((key, notification, point))