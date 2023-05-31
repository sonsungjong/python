from PySide6.QtWidgets import QApplication, QPushButton

# The slot : responds when something happends
def button_clicked(data):
    print("You clicked the button, didn't you? checked :",data)             # 파라미터로 토글의 메시지를 받아준다

app = QApplication()
button = QPushButton("Press Me")
button.setCheckable(True)           # Make the button checkable. (toggle button)

# clicked is a signal of QPushButton
# You can wire a slot to the signal using the syntax below:
button.clicked.connect(button_clicked)              # 버튼을 눌렀을 때 동작할 함수를 연결

button.show()
app.exec()
