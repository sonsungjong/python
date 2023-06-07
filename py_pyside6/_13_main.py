from PySide6.QtWidgets import QApplication
from _13_QLabel_QLineEdit import Widget
import sys

app = QApplication(sys.argv)

widget = Widget()
widget.show()

app.exec()

