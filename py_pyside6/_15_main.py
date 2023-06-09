from PySide6.QtWidgets import QApplication
from _15_QLabel_image import Widget
import sys

app = QApplication(sys.argv)

widget = Widget()
widget.show()

app.exec()