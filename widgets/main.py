#!/usr/bin/env python

import sys

from PyQt4 import QtGui

from locator import LocatorWidget, TestCommand

def main(args = None):
    app = QtGui.QApplication(sys.argv)
    locator = LocatorWidget()
    locator.addCommand(TestCommand(locator))
    locator.show()
    return app.exec_()

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))