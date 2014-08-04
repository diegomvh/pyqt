#!/usr/bin/env python

import collections

from PyQt4 import QtCore, QtGui

class Notification(QtGui.QWidget):
    aboutToClose = QtCore.pyqtSignal()
    def __init__(self, content, parent, timeout=None, icon=None, links=None):
        super(Notification, self).__init__(parent)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.horizontalLayout = QtGui.QHBoxLayout(self)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setMargin(0)

        # ------------------- Elements
        self.padding = 5
        self.border = 1
        self.radius = 5
        self.pixmap = None
        if icon is not None:
            self.pixmap = QtGui.QLabel(self)
            self.pixmap.setPixmap(icon.pixmap(
                QtCore.QSize(
                    self.pixmap.height(),
                    self.pixmap.height()
                )
            ))
            self.pixmap.setAutoFillBackground(True)
            self.pixmap.adjustSize()
            self.horizontalLayout.addWidget(self.pixmap)

        self.label = QtGui.QLabel(self)
        self.label.setText(content)
        self.label.setAutoFillBackground(True)
        self.label.adjustSize()
        self.horizontalLayout.addWidget(self.label)
        
        self.adjustSize()
        
        if links is not None:
            self.links = links
            self.label.linkActivated.connect(self.linkHandler)
        
        self._apply_style()

        self.timeoutTimer = QtCore.QTimer(self)
        self.timeoutTimer.setSingleShot(True)
        
        # ---------- Animation
        #self.shadow = QtGui.QGraphicsDropShadowEffect()
        #self.shadow.setBlurRadius(10)
        self.goe = QtGui.QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.goe)
        
        # Fade in
        self.animationIn = QtCore.QPropertyAnimation(self.goe, "opacity")
        self.animationIn.setDuration(300)
        self.animationIn.setStartValue(0)
        self.animationIn.setEndValue(1.0)

        # Fade out
        self.animationOut = QtCore.QPropertyAnimation(self.goe, "opacity")
        self.animationOut.setDuration(300)
        self.animationOut.setStartValue(1.0)
        self.animationOut.setEndValue(0)

        if timeout is not None:
            self.timeoutTimer.setInterval(timeout)
            self.animationIn.finished.connect(self.timeoutTimer.start)
            self.timeoutTimer.timeout.connect(self.close)
    
    def _apply_style(self):
        label_style =  "; ".join((
            "border: %dpx solid;" % self.border,
            "padding: %dpx" % self.padding))
        if self.pixmap is not None:
            self.pixmap.setStyleSheet("; ".join((
                "border: %dpx solid" % self.border,
                "border-right: 0px", 
                "padding: %dpx" % self.padding,
                "border-top-left-radius: %dpx" % self.radius,
                "border-bottom-left-radius: %dpx" % self.radius
            )))
            label_style = "; ".join((
                label_style,
                "border-left: 0px", 
                "border-top-right-radius: %dpx" % self.radius,
                "border-bottom-right-radius: %dpx" % self.radius
            ))
        else:
            label_style = "; ".join((
                label_style,
                "border-radius: %dpx" % self.radius))
        self.label.setStyleSheet(label_style)
        
    def setPalette(self, palette):
        super(Notification, self).setPalette(palette)
        self._apply_style()
        self.label.setPalette(palette)
        if self.pixmap is not None:
            self.pixmap.setPalette(palette)

    def show(self):
        self.setWindowOpacity(0.0)
        super(Notification, self).show()
        self.animationIn.start()
    
    def close(self):
        self.aboutToClose.emit()
        self.animationOut.finished.connect(super(Notification, self).close)
        self.animationOut.start()
    
    def linkHandler(self, link):
        callback = self.links.get(link, None)
        if isinstance(callback, collections.Callable):
            callback()

    def width(self):
        return self.label.width() + (self.pixmap and self.pixmap.width() or 0)
        
    def height(self):
        return self.label.height()
    
    def enterEvent(self, event):
        if self.timeoutTimer.isActive():
            self.timeoutTimer.stop()
    
    def leaveEvent(self, event):
        self.timeoutTimer.start()

class OverlayNotifier(QtCore.QObject):
    margin = 10
    def __init__(self, parent = None):
        super(OverlayNotifier, self).__init__(parent)
        parent.installEventFilter(self)
        self.notifications = []
        self.palette = parent.palette()
        self.palette.setColor(QtGui.QPalette.Window, QtCore.Qt.red)
        self.palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.red)
        
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Resize:
            self._fix_positions()
        return super(OverlayNotifier, self).eventFilter(obj, event)

    def _remove_notification(self):
        notification = self.sender()
        notification.aboutToClose.disconnect(self._remove_notification)
        self.notifications.remove(notification)
        self._fix_positions()
        
    def _fix_positions(self):
        offset = self.margin
        rect = self.parent().geometry()
        for notification in self.notifications:
            x = rect.width() - notification.width() - self.margin
            y = rect.height() - notification.height() - offset
            notification.setGeometry(x, y,
                notification.width(),
                notification.height())
            offset += (notification.height() + self.margin)

    def _notification(self, message, title="", frmt="text", timeout=2000, icon=None,
        links={}):
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
        
        notification = Notification(message, self.parent(), timeout, icon, links)
        notification.setPalette(self.palette)
        return notification
        
    def message(self, *args, **kwargs):
        notification = self._notification(*args, **kwargs)
        notification.aboutToClose.connect(self._remove_notification)
        self.notifications.insert(0, notification)
        return notification

    def status(self, *args, **kwargs):
        notification = self._notification(*args, **kwargs)
        notification.aboutToClose.connect(self._remove_notification)
        self.notifications.insert(0, notification)
        return notification

    def tooltip(self, *args, **kwargs):
        point = kwargs.pop("point", QtCore.QPoint(self.margin,self.margin))
        notification = self._notification(*args, **kwargs)
        notification.setGeometry(point.x(), point.y(),
            notification.width(), notification.height())
        return notification
