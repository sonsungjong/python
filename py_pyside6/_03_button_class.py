import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton

# Subclass QMainWindow to customize your application's main window
class ButtonHolder3(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BUtton Holder app")
        button = QPushButton("Press Me~")
        
        # Set our button as the central widget
        self.setCentralWidget(button)

app = QApplication(sys.argv)
window = ButtonHolder3()            # 버튼 추가
window.show()
app.exec()

