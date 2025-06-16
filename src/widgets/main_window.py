import asyncio

import azure.cognitiveservices.speech as speechsdk
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from azure_service import speech_synthesizer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VocalScript")
        self.setCentralWidget(QWidget(self))
        self.setStatusBar(QStatusBar(self))

        self.input_field: QPlainTextEdit = QPlainTextEdit(self)

        submit_button = QPushButton("Save", self)
        submit_button.setIcon(QIcon("resources/download.svg"))
        _ = submit_button.clicked.connect(
            lambda: asyncio.create_task(self.__on_submit())
        )

        main_layout: QVBoxLayout = QVBoxLayout()
        main_layout.addWidget(self.input_field)
        main_layout.addWidget(submit_button)
        self.centralWidget().setLayout(main_layout)

    async def __on_submit(self):
        speech_synthesis_result = await asyncio.to_thread(
            speech_synthesizer.speak_text, self.input_field.toPlainText()
        )

        if (
            speech_synthesis_result.reason
            == speechsdk.ResultReason.SynthesizingAudioCompleted
        ):
            msg = "Completed"
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details

            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                msg = f"Error: {cancellation_details.error_details}"
            else:
                msg = f"Canceled: {cancellation_details.reason}"
        else:
            msg = f"Unexpected result: {speech_synthesis_result.reason}"

        self.statusBar().showMessage(msg)
