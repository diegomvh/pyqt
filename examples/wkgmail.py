#!/usr/bin/env python
import sys

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import QtWebKit

javaScriptLogin = """
document.getElementsByName('Email').item(0).value='{email}';
document.getElementsByName('Passwd').item(0).value='{password}';
document.getElementsByName('signIn').item(0).click(); void(0);
"""

class GmailWebView(QtWebKit.QWebView):
    def __init__(self, parent=None):
        super(GmailWebView, self).__init__(parent)
        self.loggedIn = False

    def login(self, url, email, password):
        """Login to gmail."""
        self.url = QtCore.QUrl(url)
        self.email = email
        self.password = password  
        self.loadFinished.connect(self._loadFinished)
        self.load(self.url)

    def createWindow(self, windowType):
        """Load links in the same web-view."""
        return self

    def _loadFinished(self):
        if self.loggedIn:
            self.loadFinished.disconnect(self._loadFinished)

        self.loggedIn = True
        jscript = javaScriptLogin.format(email=self.email, password=self.password)
        self.page().mainFrame().evaluateJavaScript(jscript)

    def contextMenuEvent(self, event):
        """Add a 'Back to GMail' entry."""
        menu = self.page().createStandardContextMenu()
        menu.addSeparator()
        action = menu.addAction('Back to GMail')
        @action.triggered.connect
        def backToGMail():
            self.load(self.url)
        menu.exec_(QtGui.QCursor.pos())

def main(args = None):
    qApp = QtGui.QApplication(args)

    email, ok = QtGui.QInputDialog.getText(None, 
        "Email request", "Enter email")
    if not ok:
        return

    password, ok = QtGui.QInputDialog.getText(None, 
        "Password request", "Enter password", QtGui.QLineEdit.Password)
    if not ok:
        return

    gmailWebView = GmailWebView()
    gmailWebView.login('https://mail.google.com/mail',
                       email,
                       password)
    gmailWebView.show()

    return qApp.exec_()

if __name__ == "__main__":
    sys.exit(main(sys.argv))
