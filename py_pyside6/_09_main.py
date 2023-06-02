from PySide6.QtWidgets import QApplication, QWidget
from _09_rock_widget import RockWidget
import sys

app = QApplication(sys.argv)

# widget = QWidget()
widget = RockWidget()
widget.show()

app.exec()
