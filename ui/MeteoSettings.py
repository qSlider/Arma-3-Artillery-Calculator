from PyQt5.QtWidgets import QDialog, QFormLayout, QSpinBox, QDoubleSpinBox, QPushButton

class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Settings")
        self.setFixedSize(300, 200)

        self.temperature_input = QDoubleSpinBox()
        self.temperature_input.setSuffix(" °C")
        self.temperature_input.setRange(-50, 50)

        self.pressure_input = QDoubleSpinBox()
        self.pressure_input.setSuffix(" hPa")
        self.pressure_input.setRange(800, 1100)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.save_settings)

        # Layout
        layout = QFormLayout()
        layout.addRow("Temperature:", self.temperature_input)
        layout.addRow("Pressure:", self.pressure_input)
        layout.addRow(self.ok_button)

        self.setLayout(layout)

    def save_settings(self):
        temperature = self.temperature_input.value()
        pressure = self.pressure_input.value()
        if self.parent() is not None:
            self.parent().save_additional_settings(temperature, pressure)
        self.accept()
