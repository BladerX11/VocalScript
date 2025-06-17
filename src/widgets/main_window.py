from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from azure_service import speech_synthesizer
from widgets.status_bar import StatusBar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VocalScript")
        self.setCentralWidget(QWidget(self))
        self.setStatusBar(StatusBar(self))

        self.input_field: QPlainTextEdit = QPlainTextEdit(self)

        submit_button = QPushButton("Save", self)
        submit_button.setIcon(QIcon("resources/download.svg"))
        _ = submit_button.clicked.connect(
            lambda: speech_synthesizer.speak_text_async(self.input_field.toPlainText())
        )

        main_layout: QVBoxLayout = QVBoxLayout()
        main_layout.addWidget(self.input_field)
        main_layout.addWidget(submit_button)
        self.centralWidget().setLayout(main_layout)
