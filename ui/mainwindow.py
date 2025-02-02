import json
from PyQt5.QtWidgets import (QMainWindow, QComboBox, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QTextEdit, QCheckBox)
from logic.distanceLogic import calculate_distance, calculate_azimuth
from logic.balisticLogic import calculate_elevation_with_height, calculate_high_elevation
from mapwindow import MapWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Artillery Calculator")
        self.resize(800, 600)

        # Load JSON data
        self.data = self.load_json("config.json")

        # UI elements
        self.artillery_label = QLabel("Artillery:")
        self.artillery_combo = QComboBox()
        self.artillery_combo.addItems([system["name"] for system in self.data.get("artillerySystems", [])])
        self.artillery_combo.currentIndexChanged.connect(self.update_shells)

        self.shell_label = QLabel("Shell:")
        self.shell_combo = QComboBox()
        self.shell_combo.currentIndexChanged.connect(self.update_charges)

        self.charge_label = QLabel("Charge:")
        self.charge_combo = QComboBox()

        self.high_arc_checkbox = QCheckBox("High Arc")

        self.artillery_position_label = QLabel("Artillery Position:")
        self.artillery_x = QLineEdit()
        self.artillery_x.setPlaceholderText("X")
        self.artillery_y = QLineEdit()
        self.artillery_y.setPlaceholderText("Y")
        self.artillery_h = QLineEdit()
        self.artillery_h.setPlaceholderText("H")

        self.target_position_label = QLabel("Target Position:")
        self.target_x = QLineEdit()
        self.target_x.setPlaceholderText("X")
        self.target_y = QLineEdit()
        self.target_y.setPlaceholderText("Y")
        self.target_h = QLineEdit()
        self.target_h.setPlaceholderText("H")

        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.clicked.connect(self.calculate_solution)

        self.map_button = QPushButton("Map")
        self.map_button.clicked.connect(self.open_map_window)

        self.solutions_label = QLabel("Solutions:")
        self.solutions_text = QTextEdit()

        # Layouts
        main_layout = QVBoxLayout()
        artillery_layout = QHBoxLayout()
        shell_layout = QHBoxLayout()
        charge_layout = QHBoxLayout()
        position_layout = QHBoxLayout()
        artillery_position_layout = QVBoxLayout()
        target_position_layout = QVBoxLayout()
        buttons_layout = QHBoxLayout()

        artillery_layout.addWidget(self.artillery_label)
        artillery_layout.addWidget(self.artillery_combo)

        shell_layout.addWidget(self.shell_label)
        shell_layout.addWidget(self.shell_combo)

        charge_layout.addWidget(self.charge_label)
        charge_layout.addWidget(self.charge_combo)
        charge_layout.addWidget(self.high_arc_checkbox)

        artillery_position_layout.addWidget(self.artillery_position_label)
        artillery_position_layout.addWidget(self.artillery_x)
        artillery_position_layout.addWidget(self.artillery_y)
        artillery_position_layout.addWidget(self.artillery_h)

        target_position_layout.addWidget(self.target_position_label)
        target_position_layout.addWidget(self.target_x)
        target_position_layout.addWidget(self.target_y)
        target_position_layout.addWidget(self.target_h)

        position_layout.addLayout(artillery_position_layout)
        position_layout.addLayout(target_position_layout)

        buttons_layout.addWidget(self.calculate_button)
        buttons_layout.addWidget(self.map_button)

        main_layout.addLayout(artillery_layout)
        main_layout.addLayout(shell_layout)
        main_layout.addLayout(charge_layout)
        main_layout.addLayout(position_layout)
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.solutions_label)
        main_layout.addWidget(self.solutions_text)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.update_shells()

    def open_map_window(self):
        self.map_window = MapWindow()
        self.map_window.show()

    def load_json(self, filepath):
        try:
            with open(filepath, 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading JSON: {e}")
            return {"artillerySystems": []}

    def update_shells(self):
        self.shell_combo.clear()
        selected_artillery = self.artillery_combo.currentText()
        for system in self.data.get("artillerySystems", []):
            if system["name"] == selected_artillery:
                shells = system.get("compatibleShells", [])
                self.shell_combo.addItems([shell["name"] for shell in shells])
                break
        self.update_charges()

    def update_charges(self):
        self.charge_combo.clear()
        selected_system = self.artillery_combo.currentText()
        selected_shell = self.shell_combo.currentText()

        for system in self.data["artillerySystems"]:
            if system["name"] == selected_system:
                for shell in system["compatibleShells"]:
                    if shell["name"] == selected_shell:
                        for charge_name, charge_value in shell["charges"].items():
                            self.charge_combo.addItem(charge_name, charge_value)
                        return

    def calculate_solution(self):
        try:
            x1 = float(self.artillery_x.text())
            y1 = float(self.artillery_y.text())
            h1 = float(self.artillery_h.text())
            x2 = float(self.target_x.text())
            y2 = float(self.target_y.text())
            h2 = float(self.target_h.text())

            distance = calculate_distance(x1, y1, x2, y2)
            azimuth = calculate_azimuth(x1, y1, x2, y2)

            selected_charge_value = self.charge_combo.currentData()
            if selected_charge_value is None:
                raise ValueError("No charge selected")

            # Вибір логіки залежно від стану чекбокса
            if self.high_arc_checkbox.isChecked():
                elevation = calculate_high_elevation(distance, selected_charge_value, h1, h2)
            else:
                elevation = calculate_elevation_with_height(distance, selected_charge_value, h1, h2)

            solution_text = (
                f"Distance: {distance:.2f} m\n"
                f"Azimuth: {azimuth:.2f} thousandths\n"
                f"Elevation: {elevation:.2f} MIL"
            )
            self.solutions_text.setText(solution_text)
        except ValueError as e:
            self.solutions_text.setText(f"Error: {e}")
        except Exception as e:
            self.solutions_text.setText(f"An error occurred: {e}")


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
