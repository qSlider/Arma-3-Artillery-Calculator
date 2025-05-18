import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
                             QHeaderView, QPushButton, QMessageBox, QCheckBox, QWidget, QHBoxLayout)
from PyQt5.QtCore import Qt
import csv

try:
    from nero.datacollection import create_csv_if_not_exists, FILENAME, FIELDS
except ImportError:
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from datacollection import create_csv_if_not_exists, FILENAME, FIELDS


class SavedSolutionsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Saved Solutions")
        self.resize(800, 400)
        self.parent_window = parent

        self.layout = QVBoxLayout()

        # Create table for saved solutions
        self.table = QTableWidget()
        self.table.setColumnCount(13)
        self.table.setHorizontalHeaderLabels(
            ["Name", "Artillery", "Shell", "Charge", "Distance", "Azimuth",
             "Elevation", "Deviation(1 mil)", "ΔDeviation(1 mil)", "Hit",
             "Air Friction", "Temperature", "Pressure"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Fill table with saved solutions
        self.refresh_table()

        # Buttons
        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_selected)

        self.parse_button = QPushButton("Parsing Data")
        self.parse_button.clicked.connect(self.parse_data)

        self.layout.addWidget(self.table)
        self.layout.addWidget(self.delete_button)
        self.layout.addWidget(self.parse_button)

        self.setLayout(self.layout)

    def refresh_table(self):
        self.table.setRowCount(0)
        if not self.parent_window or not hasattr(self.parent_window, 'saved_solutions'):
            return

        row = 0
        for name, solution in self.parent_window.saved_solutions.items():
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(solution.get("artillery", "")))
            self.table.setItem(row, 2, QTableWidgetItem(solution.get("shell", "")))
            self.table.setItem(row, 3, QTableWidgetItem(solution.get("charge", "")))
            self.table.setItem(row, 4, QTableWidgetItem(solution.get("distance", "")))
            self.table.setItem(row, 5, QTableWidgetItem(solution.get("azimuth", "")))
            self.table.setItem(row, 6, QTableWidgetItem(solution.get("elevation", "")))
            self.table.setItem(row, 7, QTableWidgetItem(solution.get("deviation(1 mil)", "")))
            self.table.setItem(row, 8, QTableWidgetItem(solution.get("Δdeviation(1 mil)", "")))

            # Hit checkbox - column 9
            hit_checkbox = QCheckBox()
            hit_value = solution.get("hit", False)
            hit_checkbox.setChecked(hit_value == "True" or hit_value is True)
            hit_widget = QWidget()
            hit_layout = QHBoxLayout()
            hit_layout.addWidget(hit_checkbox)
            hit_layout.setAlignment(Qt.AlignCenter)
            hit_layout.setContentsMargins(0, 0, 0, 0)
            hit_widget.setLayout(hit_layout)
            self.table.setCellWidget(row, 9, hit_widget)

            # Air Friction checkbox - column 10
            air_friction_checkbox = QCheckBox()
            air_friction_value = solution.get("with_air_friction", False)
            air_friction_checkbox.setChecked(air_friction_value == "True" or air_friction_value is True)
            air_friction_widget = QWidget()
            air_friction_layout = QHBoxLayout()
            air_friction_layout.addWidget(air_friction_checkbox)
            air_friction_layout.setAlignment(Qt.AlignCenter)
            air_friction_layout.setContentsMargins(0, 0, 0, 0)
            air_friction_widget.setLayout(air_friction_layout)
            self.table.setCellWidget(row, 10, air_friction_widget)

            # Temperature and pressure as text items
            self.table.setItem(row, 11, QTableWidgetItem(str(solution.get("temperature", ""))))
            self.table.setItem(row, 12, QTableWidgetItem(str(solution.get("pressure", ""))))

            row += 1

    def delete_selected(self):
        selected_rows = set(index.row() for index in self.table.selectedIndexes())
        if not selected_rows:
            return

        selected_names = [self.table.item(row, 0).text() for row in selected_rows]

        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete {len(selected_names)} solution(s)?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            for name in selected_names:
                if name in self.parent_window.saved_solutions:
                    del self.parent_window.saved_solutions[name]

            self.parent_window.save_solutions_to_file()
            self.refresh_table()

    def parse_data(self):
        create_csv_if_not_exists()

        existing_records = set()
        if os.path.exists(FILENAME) and os.path.getsize(FILENAME) > 0:
            with open(FILENAME, mode='r', newline='') as file:
                reader = csv.DictReader(file, delimiter=';')
                for row in reader:
                    key = (
                        row.get("Artillery", ""),
                        row.get("Shell", ""),
                        row.get("Charge", ""),
                        row.get("Distance", ""),
                        row.get("Azimuth", ""),
                        row.get("Elevation", ""),
                        row.get("Hit", ""),
                        row.get("Temperature", ""),
                        row.get("Pressure", ""),
                        row.get("AirFriction", "")
                    )
                    existing_records.add(key)

        rows = self.table.rowCount()
        count = 0
        skipped = 0

        with open(FILENAME, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS, delimiter=';')

            for row in range(rows):
                hit_widget = self.table.cellWidget(row, 9)
                if not hit_widget:
                    continue

                hit_checkbox = hit_widget.findChild(QCheckBox)
                if hit_checkbox is None:
                    continue


                artillery = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
                shell = self.table.item(row, 2).text() if self.table.item(row, 2) else ""
                charge = self.table.item(row, 3).text() if self.table.item(row, 3) else ""
                distance = self.table.item(row, 4).text() if self.table.item(row, 4) else ""
                azimuth = self.table.item(row, 5).text() if self.table.item(row, 5) else ""
                elevation = self.table.item(row, 6).text() if self.table.item(row, 6) else ""
                hit = "True" if hit_checkbox.isChecked() else "False"
                temperature = self.table.item(row, 11).text() if self.table.item(row, 11) else ""
                pressure = self.table.item(row, 12).text() if self.table.item(row, 12) else ""
                air_friction = "True" if self._is_checkbox_checked(row, 10) else "False"

                # Check dublicate
                record_key = (
                    artillery, shell, charge, distance, azimuth,
                    elevation, hit, temperature, pressure, air_friction
                )

                if record_key in existing_records:
                    skipped += 1
                    continue

                # Add CRM Table
                record = {
                    "Artillery": artillery,
                    "Shell": shell,
                    "Charge": charge,
                    "Distance": distance,
                    "Azimuth": azimuth,
                    "Elevation": elevation,
                    "Hit": hit,
                    "Temperature": temperature,
                    "Pressure": pressure,
                    "AirFriction": air_friction
                }

                writer.writerow(record)
                existing_records.add(record_key)
                count += 1

        message = f"[✔] Successfully added {count} note(s) to CSV."
        if skipped > 0:
            message += f"\nMissing duplicates: {skipped}"

        QMessageBox.information(self, "Parsing Complete", message)

    def _is_checkbox_checked(self, row, column):
        widget = self.table.cellWidget(row, column)
        if not widget:
            return False
        checkbox = widget.findChild(QCheckBox)
        return checkbox.isChecked() if checkbox else False

    def closeEvent(self, event):
        if hasattr(self.parent_window, 'saved_solutions_dialog'):
            self.parent_window.saved_solutions_dialog = None
        event.accept()