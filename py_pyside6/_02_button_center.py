# pip install pyside6
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton

import sys

app = QApplication(sys.argv)

# 다이얼로그 박스를 띄운다
window = QMainWindow()
window.setWindowTitle("Out first MainWindow App!")              # 애플리케이션의 제목

button = QPushButton()
button.setText("Press Me")              # 버튼 캡션

window.setCentralWidget(button)

# 애플리케이션을 실행하고 이벤트 루프 시작
window.show()
app.exec()
