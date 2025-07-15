from typing import override

from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QShowEvent
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

    status: Signal = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Settings")

        self.selected_service: Services
        self.inputs: dict[str, QLineEdit] = {}
        self.field_keys: dict[str, str] = {}

        self.service_selector: QComboBox = QComboBox(self)

        for service in Services:
            self.service_selector.addItem(service.name.capitalize(), service)

        _ = self.service_selector.currentIndexChanged.connect(self.on_service_changed)

        form: QWidget = QWidget(self)
        self.form_layout: QFormLayout = QFormLayout()
        self.form_layout.addRow("&Service", self.service_selector)
        form.setLayout(self.form_layout)
        self.reset_form()

        buttons = QDialogButtonBox(
            (
                QDialogButtonBox.StandardButton.Save
                | QDialogButtonBox.StandardButton.Cancel
            ),
            self,
        )
        _ = buttons.accepted.connect(self.accept)
        _ = buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def build_form(self):
        """Builds the form fields for the selected service."""
        self.inputs.clear()
        self.field_keys.clear()
        fields = TtsService.get_setting_fields_for(self.selected_service)

        while self.form_layout.rowCount() > 1:
            self.form_layout.removeRow(1)

        for field in fields:
            editor = QLineEdit(self)
            key = f"{self.selected_service.value}/{field}"
            editor.setText(str(settings.value(key, "")))
            self.inputs[field] = editor
            self.field_keys[field] = key
            self.form_layout.addRow(f"&{field.capitalize()}", editor)

    @Slot(int)
    def on_service_changed(self, index: int):
        """Updates selected service and rebuilds fields."""
        self.selected_service = self.service_selector.itemData(index)
        self.build_form()

    def reset_form(self):
        """
        Reset form fields based on saved service in QSettings. Uses default for new users.
        """
        try:
            service = Services(settings.value("service"))
        except ValueError:
            self.status.emit(
                "Loading saved service failed. Invalid service. Using default service."
            )
            service = TtsService.DEFAULT_SERVICE

        self.selected_service = service
        self.service_selector.setCurrentIndex(
            self.service_selector.findData(self.selected_service)
        )
        self.build_form()

    @override
    def showEvent(self, event: QShowEvent):
        """Reset form to saved settings when dialog is shown"""
        self.reset_form()
        super().showEvent(event)

    @override
    def accept(self):
        for field, editor in self.inputs.items():
            value = editor.text()
            settings.setValue(self.field_keys[field], value)

        settings.setValue("service", self.selected_service.value)
        super().accept()
