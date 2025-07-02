from typing import override

from azure.cognitiveservices.speech import PropertyId
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from azure_service import speech_synthesizer
from settings import settings


class Settings(QDialog):
    """Dialog to configure speech service key and endpoint settings."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Settings")

        self.key_input: QLineEdit = QLineEdit(self)
        self.key_input.setText(settings.value("key"))
        self.endpoint_input: QLineEdit = QLineEdit(self)
        self.endpoint_input.setText(settings.value("endpoint"))

        form_layout = QFormLayout(self)
        form_layout.addRow("&Key", self.key_input)
        form_layout.addRow("&Endpoint", self.endpoint_input)

        form = QWidget(self)
        form.setLayout(form_layout)

        buttons = QDialogButtonBox(
            (
                QDialogButtonBox.StandardButton.Save
                | QDialogButtonBox.StandardButton.Cancel
            )
        )
        _ = buttons.accepted.connect(self.accept)
        _ = buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    @override
    def accept(self):
        """Save the entered key and endpoint to persistent settings and update synthesizer properties."""
        new_key = self.key_input.text()
        new_endpoint = self.endpoint_input.text()
        settings.setValue("key", new_key)
        settings.setValue("endpoint", new_endpoint)
        properties = speech_synthesizer.properties
        properties.set_property(PropertyId.SpeechServiceConnection_Key, new_key)
        properties.set_property(
            PropertyId.SpeechServiceConnection_Endpoint, new_endpoint
        )
        super().accept()
