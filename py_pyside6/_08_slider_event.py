from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QSlider

# The slot : responds when something happens
def respond_to_slider(data):
    print("slider moved to :", data)

app = QApplication()
slider = QSlider(Qt.Horizontal)             # 수평 슬라이더
slider.setMinimum(1)                # 최소값
slider.setMaximum(100)              # 최대값
slider.setValue(25)                 # 값 셋팅

# event connect
slider.valueChanged.connect(respond_to_slider)          # 값변경 이벤트를 함수와 연결

# run
slider.show()
app.exec()
