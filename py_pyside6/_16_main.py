from PySide6.QtWidgets import QApplication
from _16_size_policies import Widget
import sys

app = QApplication(sys.argv)

widget = Widget()
widget.show()

app.exec()