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
        self._inputs: dict[str, QLineEdit] = {}
        self._field_keys: dict[str, str] = {}

        self._service_selector: QComboBox = QComboBox(self)

        for service in Services:
            self._service_selector.addItem(service.name.capitalize(), service)

        _ = self._service_selector.currentIndexChanged.connect(self.on_service_changed)

        form: QWidget = QWidget(self)
        self._form_layout: QFormLayout = QFormLayout()
        self._form_layout.addRow("&Service", self._service_selector)
        form.setLayout(self._form_layout)
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
        self._inputs.clear()
        self._field_keys.clear()
        service_settings = TtsService.get_service_class(
            self.selected_service
        ).setting_fields()

        while self._form_layout.rowCount() > 1:
            self._form_layout.removeRow(1)

        for setting in service_settings:
            editor = QLineEdit(self)
            name = setting.name
            key = setting.key
            editor.setText(str(settings.value(key, "")))
            self._inputs[name] = editor
            self._field_keys[name] = key
            self._form_layout.addRow(f"&{name.capitalize()}", editor)

    @Slot(int)
    def on_service_changed(self, index: int):
        """Updates selected service and rebuilds fields."""
        self.selected_service = self._service_selector.itemData(index)
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
        self._service_selector.setCurrentIndex(
            self._service_selector.findData(self.selected_service)
        )
        self.build_form()

    @override
    def showEvent(self, event: QShowEvent):
        """Reset form to saved settings when dialog is shown"""
        self.reset_form()
        super().showEvent(event)

    @override
    def accept(self):
        for field, editor in self._inputs.items():
            value = editor.text()
            settings.setValue(self._field_keys[field], value)

        settings.setValue("service", self.selected_service.value)
        super().accept()
