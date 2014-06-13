#!/usr/bin/env python

#Before impoort PyQt
import sip
sip.setapi('QString', 2)

def locator_widget():
    from PyQt4 import QtGui
    from locator import LocatorWidget, OpenCommand
    
    locator = LocatorWidget()
    locator.addCommand(OpenCommand(locator))
    return locator

def awesome_icons():
    import os
    import random
    
    from PyQt4 import QtCore, QtGui
    from awesome import QtAwesome, FONTAWESOMECODES
    
    aws = QtAwesome()

    ttf_path = os.path.abspath("../resources/fonts/fontawesome-4.1.0.ttf")
    aws.initFontAwesome(ttf_path)

    codekeys = [key for key in FONTAWESOMECODES.keys()]
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
    from PyQt4 import QtGui
        
    app = QtGui.QApplication(sys.argv)
    
    locator = locator_widget()
    button = awesome_icons()
    button.show()
    locator.show()
    
    return app.exec_()

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))