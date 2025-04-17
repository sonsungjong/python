# python.exe -m pip install --upgrade pip
# pip install pyside6
# pip install pyinstaller

# pyinstaller --onefile --windowed --hidden-import=PySide6.QtWebEngineWidgets --add-binary "C:\Python312\Lib\site-packages\PySide6\QtWebEngineProcess.exe;." --add-data "C:\Python312\Lib\site-packages\PySide6\resources;resources" --add-data "C:\Python312\Lib\site-packages\PySide6\translations;translations" web.py


from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit
from PySide6.QtWebEngineWidgets import QWebEngineView
import sys

class SimpleBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("웹브라우저")
        self.setGeometry(100, 100, 1200, 800)

        # 메인 위젯 구성
        self.browser = QWebEngineView()
        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("URL을 입력하세요... (예: https://google.com)")
        self.address_bar.returnPressed.connect(self.load_url)

        layout = QVBoxLayout()
        layout.addWidget(self.address_bar)
        layout.addWidget(self.browser)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 기본 페이지 열기
        self.browser.setUrl("https://google.com")

    def load_url(self):
        url = self.address_bar.text()
        if not url.startswith("http"):
            url = "http://" + url
        self.browser.setUrl(url)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleBrowser()
    window.show()
    sys.exit(app.exec())