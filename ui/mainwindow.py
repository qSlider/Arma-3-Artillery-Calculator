import sys
import json , os
from PyQt5.QtWidgets import (QMainWindow, QComboBox, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QHBoxLayout,
                             QTextEdit, QCheckBox, QMessageBox)
from logic.distanceLogic import calculate_distance, calculate_azimuth
from logic.balisticLogic import calculate_elevation_with_height, calculate_high_elevation
from mapwindow import MapWindow
from ui.MeteoSettings import SettingsWindow
from logic.balisticLogicAirFriction import find_optimal_angle, degrees_to_mil , find_high_trajectory



sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Artillery Calculator")
        self.resize(800, 600)

        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.json')
        self.data = self.load_json(self.config_path)

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

        self.air_friction_checkbox = QCheckBox("Air Friction")
        self.air_friction_checkbox.stateChanged.connect(self.toggle_air_friction)

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

        self.settings_button = QPushButton("Meteo")
        self.settings_button.clicked.connect(self.open_meteo_settings)

        self.solutions_label = QLabel("Solutions:")
        self.solutions_text = QTextEdit()

        self.temperature = 15.0  # default
        self.pressure = 1013.25  # default
        self.k_base = 1.0  # default



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
        charge_layout.addWidget(self.air_friction_checkbox)

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
        buttons_layout.addWidget(self.settings_button)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.update_shells()

    def toggle_air_friction(self, state):
        """Реакция на изменение состояния чекбокса"""
        if state:
            print("Air Friction включен")
        else:
            print("Air Friction выключен")

    def open_map_window(self):
        try:
            self.map_window = MapWindow()
            # Подключаем отдельные сигналы
            self.map_window.artillery_coordinates_selected.connect(self.update_artillery_position)
            self.map_window.target_coordinates_selected.connect(self.update_target_position)
            self.map_window.show()
        except Exception as e:
            self.show_error(f"Error opening map window: {e}")

    def open_meteo_settings(self):
        self.meteo_window = SettingsWindow(self)
        self.meteo_window.exec_()

    def update_coordinates_from_map(self, artillery_coords, target_coords, artillery_h, target_h):
        try:
            if isinstance(artillery_coords, tuple):
                self.artillery_y.setText(f"{artillery_coords[0]:.2f}")
                self.artillery_x.setText(f"{artillery_coords[1]:.2f}")
                self.artillery_h.setText(f"{artillery_h:.2f}")

            if isinstance(target_coords, tuple):
                self.target_y.setText(f"{target_coords[0]:.2f}")
                self.target_x.setText(f"{target_coords[1]:.2f}")
                self.target_h.setText(f"{target_h:.2f}")
        except Exception as e:
            self.show_error(f"Ошибка обновления координат: {e}")

    def update_artillery_position(self, artillery_coords, artillery_h):
        try:
            if isinstance(artillery_coords, tuple):
                self.artillery_y.setText(f"{artillery_coords[0]:.2f}")
                self.artillery_x.setText(f"{artillery_coords[1]:.2f}")
                self.artillery_h.setText(f"{artillery_h:.2f}")
        except Exception as e:
            self.show_error(f"Ошибка обновления артиллерии: {e}")

    def update_target_position(self, target_coords, target_h):
        try:
            if isinstance(target_coords, tuple):
                self.target_y.setText(f"{target_coords[0]:.2f}")
                self.target_x.setText(f"{target_coords[1]:.2f}")
                self.target_h.setText(f"{target_h:.2f}")
        except Exception as e:
            self.show_error(f"Ошибка обновления цели: {e}")

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

    def fill_coordinates_from_map(self):
        if hasattr(self, 'map_window') and self.map_window is not None:
            coordinates = self.map_window.get_coordinates()
            if coordinates:
                self.update_coordinates_from_map(coordinates)
        else:
            self.solutions_text.setText("Map window is not open.")

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

    def save_additional_settings(self, temperature, pressure):
        self.temperature = temperature
        self.pressure = pressure

    def update_charges(self):
        self.charge_combo.clear()
        selected_system = self.artillery_combo.currentText()
        selected_shell = self.shell_combo.currentText()

        for system in self.data["artillerySystems"]:
            if system["name"] == selected_system:
                self.k_base = abs(system["k_base"])
                for shell in system["compatibleShells"]:
                    if shell["name"] == selected_shell:
                        self.charge_speed = shell["chargeSpeed"]
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
                raise ValueError("Заряд не выбран")

            charge_speed = selected_charge_value
            elevation = None

            if self.air_friction_checkbox.isChecked():
                # Получаем состояние High Arc
                high_arc = self.high_arc_checkbox.isChecked()
                elevation = self.calculate_trajectory_with_air(
                    distance,
                    charge_speed,
                    h1,
                    h2,
                    self.temperature,
                    self.pressure,
                    self.k_base,
                    high_arc=high_arc  # Передаем флаг High Arc
                )
                if elevation is None:
                    raise ValueError("Не удалось найти угол с учетом сопротивления воздуха")
            else:
                # Базовая логика без сопротивления воздуха
                if self.high_arc_checkbox.isChecked():
                    elevation = calculate_high_elevation(distance, selected_charge_value, h1, h2)
                else:
                    elevation = calculate_elevation_with_height(distance, selected_charge_value, h1, h2)

            solution_text = (
                f"Distance: {distance:.2f} м\n"
                f"Azimuth: {azimuth:.2f} mil\n"
                f"Elevation: {elevation:.2f} MIL"
            )
            if self.air_friction_checkbox.isChecked():
                solution_text += "\n(Air Friction)"

            self.solutions_text.setText(solution_text)

        except ValueError as e:
            self.solutions_text.setText(f"Error: {e}")
        except Exception as e:
            self.solutions_text.setText(f"Error: {str(e)}")

    def calculate_trajectory_with_air(self, distance, v0, h1, h2, temperature, pressure, k_base, high_arc=False):
        height_diff = h2 - h1
        try:
            if high_arc:
                print(f"[DEBUG] Settings hight: v0={v0}, distance={distance}, height_diff={height_diff}, T={temperature}, P={pressure}, k_base={k_base}")
                angle = find_high_trajectory(
                    v0=v0,
                    distance=distance,
                    height_diff=height_diff,
                    temperature=temperature,
                    pressure=pressure,
                    k_base=k_base,
                    plot=False
                )
            else:
                print(f"[DEBUG] Settings low: v0={v0}, distance={distance}, height_diff={height_diff}, T={temperature}, P={pressure}, k_base={k_base}")
                angle = find_optimal_angle(
                    v0=v0,
                    distance=distance,
                    height_diff=height_diff,
                    temperature=temperature,
                    pressure=pressure,
                    k_base=k_base,
                    plot=False
                )

            if angle is None:
                raise ValueError("Не удалось найти угол с учетом сопротивления воздуха")

            return degrees_to_mil(angle)

        except Exception as e:
            self.show_error(f"Помилка розрахунку: {str(e)}")
            return None



def create_folders():
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    folders = [
        os.path.join(base_dir, "map", "data"),
        os.path.join(base_dir, "map", "img")
    ]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)


if __name__ == "__main__":
    create_folders()
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())