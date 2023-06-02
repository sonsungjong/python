from PySide6.QtWidgets import QApplication
from _10_mainwindow import MyMainWindow
import sys

app = QApplication(sys.argv)

window = MyMainWindow(app)
window.show()

app.exec()