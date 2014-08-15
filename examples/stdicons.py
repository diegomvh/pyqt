#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

def get_std_icon(name):
    if not name.startswith('SP_'):
        name = 'SP_' + name
    standardIconName = getattr(QtGui.QStyle, name, None)
    if standardIconName is not None:
        return QtGui.QWidget().style().standardIcon( standardIconName )

class ShowStdIcons(QtGui.QWidget):
    """
    Dialog showing standard icons
    """
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QHBoxLayout()
        row_nb = 14
        cindex = 0
        for child in dir(QtGui.QStyle):
            if child.startswith('SP_'):
                if cindex == 0:
                    col_layout = QtGui.QVBoxLayout()
                icon_layout = QtGui.QHBoxLayout()
                icon = get_std_icon(child)
                label = QtGui.QLabel()
                label.setPixmap(icon.pixmap(16, 16))
                icon_layout.addWidget( label )
                icon_layout.addWidget( QtGui.QLineEdit(child.replace('SP_', '')) )
                col_layout.addLayout(icon_layout)
                cindex = (cindex+1) % row_nb
                if cindex == 0:
                    layout.addLayout(col_layout)                    
        self.setLayout(layout)
        self.setWindowTitle('Standard Platform Icons')
        self.setWindowIcon(get_std_icon('TitleBarMenuButton'))

def show_std_icons():
    """
    Show all standard Icons
    """
    app = QtGui.QApplication([])
    dialog = ShowStdIcons(None)
    print(get_std_icon("cacho"))
    dialog.show()
    import sys
    sys.exit(app.exec_())


if __name__ == "__main__":
    show_std_icons()