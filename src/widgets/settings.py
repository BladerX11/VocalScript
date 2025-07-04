from typing import override

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from services.tts_service import Services, TtsService
from settings import settings


class Settings(QDialog):
    """Dialog to configure speech service key and endpoint settings."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Settings")

        self.selected_service: Services = TtsService.get_service().type()
        self.inputs: dict[str, QLineEdit] = {}
        self.field_keys: dict[str, str] = {}

        self.service_selector: QComboBox = QComboBox(self)

        for service in Services:
            self.service_selector.addItem(service.name.capitalize(), service)

        idx = list(Services).index(self.selected_service)
        self.service_selector.setCurrentIndex(idx)
        _ = self.service_selector.currentIndexChanged.connect(self.on_service_changed)

        self.form: QWidget = QWidget(self)
        self.build_form()

        buttons = QDialogButtonBox(
            (
                QDialogButtonBox.StandardButton.Save
                | QDialogButtonBox.StandardButton.Cancel
            )
        )
        _ = buttons.accepted.connect(self.accept)
        _ = buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self.service_selector)
        layout.addWidget(self.form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    @override
    def accept(self):
        settings.setValue("service", self.selected_service.value)

        for field, editor in self.inputs.items():
            value = editor.text()
            settings.setValue(self.field_keys[field], value)

        TtsService.switch(self.selected_service)
        super().accept()

    def build_form(self):
        """Builds the form fields for the selected service."""
        self.inputs.clear()
        self.field_keys.clear()
        form_layout = QFormLayout()
        fields = TtsService.get_setting_fields_for(self.selected_service)

        for field in fields:
            editor = QLineEdit(self)
            key = f"{self.selected_service.value}/{field}"
            editor.setText(str(settings.value(key, "")))
            self.inputs[field] = editor
            self.field_keys[field] = key
            form_layout.addRow(f"&{field.capitalize()}", editor)

        self.form.setLayout(form_layout)

    def on_service_changed(self, index: int):
        """Updates selected service and rebuilds fields."""
        self.selected_service = self.service_selector.itemData(index)
        self.build_form()
