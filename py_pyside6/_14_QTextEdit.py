from PySide6.QtWidgets import QWidget, QTextEdit, QHBoxLayout, QPushButton, QVBoxLayout

class Widget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QTextEdit demo")

        self.text_edit = QTextEdit()
        # self.text_edit.textChanged.connect(self.text_changed)

        # Buttons

        current_text_button = QPushButton("Current Text")
        current_text_button.clicked.connect(self.current_text_button_clicked)

        copy_button = QPushButton("Copy")
        copy_button.clicked.connect(self.text_edit.copy)

        cut_button = QPushButton("Cut")
        cut_button.clicked.connect(self.text_edit.cut)

        paste_button = QPushButton("Paste")
        paste_button.clicked.connect(self.paste)

        undo_button = QPushButton("Undo")
        undo_button.clicked.connect(self.text_edit.undo)

        redo_button = QPushButton("Redo")
        redo_button.clicked.connect(self.text_edit.redo)

        set_plain_text_button = QPushButton("set Plain Text")
        set_plain_text_button.clicked.connect(self.set_plain_text)

        set_html_button = QPushButton("Set html")
        set_html_button.clicked.connect(self.set_html)

        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.text_edit.clear)

        h_layout = QHBoxLayout()
        h_layout.addWidget(current_text_button)
        h_layout.addWidget(copy_button)
        h_layout.addWidget(cut_button)
        h_layout.addWidget(paste_button)
        h_layout.addWidget(undo_button)
        h_layout.addWidget(redo_button)
        h_layout.addWidget(set_plain_text_button)
        h_layout.addWidget(set_html_button)
        h_layout.addWidget(clear_button)

        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout)
        v_layout.addWidget(self.text_edit)

        self.setLayout(v_layout)

    def current_text_button_clicked(self):
        print(self.text_edit.toPlainText())

    def paste(self):
        self.text_edit.paste()

    def set_plain_text(self):
        self.text_edit.setPlainText("Sed ut perspiciatis unde omnis iste natus error sit voluptate accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab li")

    def set_html(self):
        self.text_edit.setHtml("<h1>Kigali Districts</h1><p>The city of Kigali has three districts : </br> <ul> <li>Gasabo</li>  <li>Nyarugenge</li><li>Kicukiro</li></ul></p>")
    