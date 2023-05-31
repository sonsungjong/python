import sys
from PySide6.QtWidgets import QApplication
from _04_button_holder import ButtonHolder4

app = QApplication(sys.argv)

window = ButtonHolder4()
window.show()

app.exec()
