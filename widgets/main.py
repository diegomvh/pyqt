#!/usr/bin/env python

#Before impoort PyQt
import os
import sip
sip.setapi('QString', 2)

BASE_PATH = os.path.dirname(__file__)

import string

def notification():
    from PyQt4 import QtGui
    from notification import OverlayNotifier
    
    window = QtGui.QMainWindow()
    window.notifier = OverlayNotifier(window)
    return window

def locator_widget():
    from locator import LocatorWidget, OpenCommand
    
    locator = LocatorWidget()
    locator.addCommand(OpenCommand(locator))
    return locator

def glyph_icons():
    import random
    
    from PyQt4 import QtCore, QtGui
    from glyph import QtGlyph
    
    #ttf_path = os.path.abspath("../resources/fonts/fontawesome-4.1.0.ttf")
    ttf_path = os.path.abspath(
        os.path.join(BASE_PATH, "../resources/fonts/webhostinghub-glyphs.ttf"))
    aws = QtGlyph.initGlyph(ttf_path)

    codekeys = list(aws.codepoints().keys())
    if not codekeys:
        codekeys = list(string.ascii_letters)
    def random_icon():
        return aws.icon(random.choice(codekeys))
        
    pushButton = QtGui.QPushButton( random_icon(), "" )
    class IconSize(QtCore.QObject):
        def eventFilter(self, obj, event):
            if pushButton == obj and event.type() == QtCore.QEvent.Resize:
                pushButton.setIconSize( 
                    QtCore.QSize( pushButton.size().width(),
                        pushButton.size().height())
                    )
            return super(IconSize, self).eventFilter(obj, event)

    pushButton.clicked.connect(lambda : pushButton.setIcon(random_icon()))
    
    pushButton.installEventFilter(IconSize(pushButton))
    return pushButton
    
def main(args = None):
    import os
    from PyQt4 import QtGui, QtCore

    app = QtGui.QApplication(sys.argv)
    
    locator = locator_widget()
    button = glyph_icons()
    window = notification()
    button.show()
    locator.show()
    window.show()
    
    def link(text):
        def _link():
            print(text)
        return _link
    
    links = {
        "link": link("link"),
        "one": link("one")
    }
    status = window.notifier.status("Lorem ipsum dolor sit amet, consectetur adipisicing elit,\nsed do eiusmod tempor incididunt ut labore et dolore magna aliqua.", title="Notification Test", links = links)
    window.notifier.message("Lorem ipsum dolor sit amet, consectetur adipisicing elit,\nsed do eiusmod tempor incididunt ut labore et dolore magna aliqua.", title="Notification 2 Test", icon = button.icon()).show()
    window.notifier.tooltip("locator", widget=locator).show()
    window.notifier.tooltip("button", widget=button).show()
    
    window.notifier.tooltip("Lorem ipsum dolor sit amet", title="Popup", frmt="html", point = QtCore.QPoint(0,0), links = links).show()
    
    status.show()
    button.clicked.connect(lambda : status.close())
    
    return app.exec_()

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
