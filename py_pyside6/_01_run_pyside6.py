# python 3.9.15
# PySide6 (Qt For Python)
# Windows, Linux, Mac
# Android, iOS, embadded

# pip install pyside6
from PySide6.QtWidgets import QApplication, QWidget

import sys

app = QApplication(sys.argv)

window = QWidget()
window.show()

# 실행된 앱을 유지 (Start the event loop)
app.exec()
