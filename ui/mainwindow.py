import sys
import json
import os
from PyQt5.QtWidgets import (QMainWindow, QComboBox, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QHBoxLayout,
                             QTextEdit, QCheckBox, QMessageBox, QInputDialog)
from PyQt5.QtCore import Qt
from logic.distanceLogic import calculate_distance, calculate_azimuth , calculate_mils
from logic.balisticLogic import calculate_elevation_with_height, calculate_high_elevation , mil_to_rad , calculate_range , range_difference_for_1mil
from mapwindow import MapWindow
from ui.MeteoSettings import SettingsWindow
from logic.balisticLogicAirFriction import find_optimal_angle, degrees_to_mil, find_high_trajectory
from solutionwindow import SavedSolutionsWindow

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Artillery Calculator")
        self.resize(800, 600)

        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.json')
        self.data = self.load_json(self.config_path)

        # Path for saved solutions
        self.saved_solutions_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                                                 'saved_solutions.json')
        self.saved_solutions = {}
        try:
            self.saved_solutions = self.load_saved_solutions()
        except Exception as e:
            print(f"Error loading saved solutions: {e}")
            self.saved_solutions = {}

        self.next_solution_number = self.get_next_solution_number()

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

        # New buttons for saved solutions
        self.save_solution_button = QPushButton("Save Solution")
        self.save_solution_button.clicked.connect(self.save_current_solution)
        self.save_solution_button.setEnabled(False)  # Enable only after calculation

        self.saved_solutions_button = QPushButton("Saved Solutions")
        self.saved_solutions_button.clicked.connect(self.open_saved_solutions)

        self.solutions_label = QLabel("Solutions:")
        self.solutions_text = QTextEdit()
        self.solutions_text.setReadOnly(True)  # Make read-only to prevent accidental editing

        self.temperature = 15.0  # default
        self.pressure = 1013.25  # default
        self.k_base = 1.0  # default

        # Store current solution data
        self.current_solution = {}

        # Layouts
        main_layout = QVBoxLayout()
        artillery_layout = QHBoxLayout()
        shell_layout = QHBoxLayout()
        charge_layout = QHBoxLayout()
        position_layout = QHBoxLayout()
        artillery_position_layout = QVBoxLayout()
        target_position_layout = QVBoxLayout()
        buttons_layout = QHBoxLayout()
        solutions_layout = QHBoxLayout()

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
        buttons_layout.addWidget(self.settings_button)
        buttons_layout.addWidget(self.save_solution_button)
        buttons_layout.addWidget(self.saved_solutions_button)

        solutions_layout.addWidget(self.solutions_label)

        main_layout.addLayout(artillery_layout)
        main_layout.addLayout(shell_layout)
        main_layout.addLayout(charge_layout)
        main_layout.addLayout(position_layout)
        main_layout.addLayout(buttons_layout)
        main_layout.addLayout(solutions_layout)
        main_layout.addWidget(self.solutions_text)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.update_shells()

    def get_next_solution_number(self):
        """Get the next sequential solution number for auto-naming"""
        try:
            existing_names = [name for name in self.saved_solutions.keys()
                              if name.startswith('P') and name[1:].isdigit()]

            if not existing_names:
                return 1

            # Extract numbers from existing P1, P2, etc. names
            existing_numbers = [int(name[1:]) for name in existing_names]
            if existing_numbers:
                return max(existing_numbers) + 1
            else:
                return 1
        except Exception as e:
            print(f"Error getting next solution number: {e}")
            return 1

    def load_saved_solutions(self):
        """Load saved solutions from file"""
        try:
            if os.path.exists(self.saved_solutions_path):
                with open(self.saved_solutions_path, 'r') as file:
                    return json.load(file)
            return {}
        except Exception as e:
            print(f"Error loading saved solutions: {e}")
            return {}

    def save_solutions_to_file(self):
        """Save solutions to file"""
        try:
            directory = os.path.dirname(self.saved_solutions_path)
            if not os.path.exists(directory):
                os.makedirs(directory)

            with open(self.saved_solutions_path, 'w') as file:
                json.dump(self.saved_solutions, file, indent=4)
        except Exception as e:
            print(f"Error saving solutions: {e}")
            QMessageBox.warning(self, "Warning", f"Could not save solutions: {e}")

    def save_current_solution(self):
        """Save the current solution with a name"""
        if not self.current_solution:
            QMessageBox.warning(self, "Warning", "No solution to save. Calculate first.")
            return

        try:
            # Get a name for the solution
            name, ok = QInputDialog.getText(
                self, "Save Solution",
                "Enter a name for this solution (leave empty for auto-naming):"
            )

            if not ok:
                return  # User canceled

            # If empty, generate automatic name
            if not name:
                name = f"P{self.next_solution_number}"
                self.next_solution_number += 1

            # If name already exists, append a number
            original_name = name
            counter = 1
            while name in self.saved_solutions:
                name = f"{original_name}_{counter}"
                counter += 1

            # Save the solution
            self.saved_solutions[name] = self.current_solution.copy()
            self.save_solutions_to_file()

            QMessageBox.information(
                self, "Solution Saved",
                f"Solution saved as '{name}'."
            )
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save solution: {e}")

    def open_saved_solutions(self):
        try:
            self.saved_solutions_dialog = SavedSolutionsWindow(self)
            self.saved_solutions_dialog.show()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open saved solutions: {e}")

    def toggle_air_friction(self, state):
        if state:
            print("Air Friction включен")
        else:
            print("Air Friction выключен")

    def open_map_window(self):
        try:
            self.map_window = MapWindow()
            self.map_window.artillery_coordinates_selected.connect(self.update_artillery_position)
            self.map_window.target_coordinates_selected.connect(self.update_target_position)
            self.map_window.show()
        except Exception as e:
            self.show_error(f"Error opening map window: {e}")

    def open_meteo_settings(self):
        try:
            self.meteo_window = SettingsWindow(self)
            self.meteo_window.exec_()
        except Exception as e:
            self.show_error(f"Error opening meteo settings: {e}")

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
        try:
            self.shell_combo.clear()
            selected_artillery = self.artillery_combo.currentText()
            for system in self.data.get("artillerySystems", []):
                if system["name"] == selected_artillery:
                    shells = system.get("compatibleShells", [])
                    self.shell_combo.addItems([shell["name"] for shell in shells])
                    break
            self.update_charges()
        except Exception as e:
            print(f"Error updating shells: {e}")

    def save_additional_settings(self, temperature, pressure):
        self.temperature = temperature
        self.pressure = pressure

    def update_charges(self):
        try:
            self.charge_combo.clear()
            selected_system = self.artillery_combo.currentText()
            selected_shell = self.shell_combo.currentText()

            for system in self.data.get("artillerySystems", []):
                if system["name"] == selected_system:
                    self.k_base = abs(system.get("k_base", 1.0))
                    for shell in system.get("compatibleShells", []):
                        if shell["name"] == selected_shell:
                            self.charge_speed = shell.get("chargeSpeed", 0)
                            for charge_name, charge_value in shell.get("charges", {}).items():
                                self.charge_combo.addItem(charge_name, charge_value)
                            return
        except Exception as e:
            print(f"Error updating charges: {e}")

    def calculate_solution(self):
        try:
            # Reset save button
            self.save_solution_button.setEnabled(False)

            # Validate input fields
            if not all([self.artillery_x.text(), self.artillery_y.text(), self.artillery_h.text(),
                        self.target_x.text(), self.target_y.text(), self.target_h.text()]):
                self.solutions_text.setText("Error: All position fields must be filled")
                return

            try:
                x1 = float(self.artillery_x.text())
                y1 = float(self.artillery_y.text())
                h1 = float(self.artillery_h.text())
                x2 = float(self.target_x.text())
                y2 = float(self.target_y.text())
                h2 = float(self.target_h.text())
            except ValueError:
                self.solutions_text.setText("Error: Position coordinates must be valid numbers")
                return

            distance = calculate_distance(x1, y1, x2, y2)
            azimuth = calculate_azimuth(x1, y1, x2, y2)
            mils = calculate_mils(distance)

            selected_charge_value = self.charge_combo.currentData()
            if selected_charge_value is None:
                raise ValueError("Заряд не выбран")

            charge_speed = selected_charge_value
            elevation = None

            if self.air_friction_checkbox.isChecked():
                high_arc = self.high_arc_checkbox.isChecked()
                elevation = self.calculate_trajectory_with_air(
                    distance,
                    charge_speed,
                    h1,
                    h2,
                    self.temperature,
                    self.pressure,
                    self.k_base,
                    high_arc=high_arc
                )
                if elevation is None:
                    raise ValueError("Не удалось найти угол с учетом сопротивления воздуха")
                mils_delta = None
            else:
                if self.high_arc_checkbox.isChecked():
                    elevation = calculate_high_elevation(distance, selected_charge_value, h1, h2)
                else:
                    elevation = calculate_elevation_with_height(distance, selected_charge_value, h1, h2)

                mils_delta = range_difference_for_1mil(selected_charge_value, elevation, h1, h2)

            solution_text = (
                f"Distance: {distance:.2f} м\n"
                f"Azimuth: {azimuth:.2f} mil\n"
                f"Elevation: {elevation:.2f} MIL\n"
                f"Deviation (1 mil): {mils:.2f} м\n"
                f"ΔDeviation in range(1 mil): {mils_delta:.2f} м"
            )

            if self.air_friction_checkbox.isChecked():
                solution_text += "\n(Air Friction)"

            self.solutions_text.setText(solution_text)

            # Store solution details for saving
            self.current_solution = {
                "artillery": self.artillery_combo.currentText(),
                "shell": self.shell_combo.currentText(),
                "charge": self.charge_combo.currentText(),
                "distance": f"{distance:.2f} м",
                "azimuth": f"{azimuth:.2f} mil",
                "elevation": f"{elevation:.2f} MIL",
                "deviation(1 mil)": f"{mils:.2f} м",
                "Δdeviation(1 mil)": f"{mils_delta:.2f} м",
                "with_air_friction": self.air_friction_checkbox.isChecked(),
                "high_arc": self.high_arc_checkbox.isChecked(),
                "artillery_position": {
                    "x": x1,
                    "y": y1,
                    "h": h1
                },
                "target_position": {
                    "x": x2,
                    "y": y2,
                    "h": h2
                }
            }

            # Enable save button after calculation
            self.save_solution_button.setEnabled(True)

        except ValueError as e:
            self.solutions_text.setText(f"Error: {e}")
            self.save_solution_button.setEnabled(False)
        except Exception as e:
            self.solutions_text.setText(f"Error: {str(e)}")
            self.save_solution_button.setEnabled(False)

    def calculate_trajectory_with_air(self, distance, v0, h1, h2, temperature, pressure, k_base, high_arc=False):
        height_diff = h2 - h1
        try:
            if high_arc:
                print(
                    f"[DEBUG] Settings hight: v0={v0}, distance={distance}, height_diff={height_diff}, T={temperature}, P={pressure}, k_base={k_base}")
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
                print(
                    f"[DEBUG] Settings low: v0={v0}, distance={distance}, height_diff={height_diff}, T={temperature}, P={pressure}, k_base={k_base}")
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
    try:
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        folders = [
            os.path.join(base_dir, "map", "data"),
            os.path.join(base_dir, "map", "img")
        ]
        for folder in folders:
            os.makedirs(folder, exist_ok=True)
    except Exception as e:
        print(f"Error creating folders: {e}")


if __name__ == "__main__":
    try:
        create_folders()
        import sys
        from PyQt5.QtWidgets import QApplication

        app = QApplication(sys.argv)

        window = MainWindow()
        window.show()

        sys.exit(app.exec_())
    except Exception as e:
        print(f"Critical error: {e}")
        if 'app' in locals():
            QMessageBox.critical(None, "Critical Error",
                                 f"The application encountered a critical error and needs to close: {e}")