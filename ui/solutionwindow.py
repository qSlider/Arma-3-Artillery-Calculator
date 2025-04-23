import sys
import json
import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
                            QHeaderView, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt

class SavedSolutionsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Saved Solutions")
        self.resize(600, 400)
        self.parent_window = parent

        self.layout = QVBoxLayout()

        # Create table for saved solutions
        self.table = QTableWidget()
        self.table.setColumnCount(9)  # Name, Artillery, Shell, Charge, Distance, Azimuth, Elevation
        self.table.setHorizontalHeaderLabels(
            ["Name", "Artillery", "Shell", "Charge", "Distance", "Azimuth", "Elevation", "Deviation(1 mil)","ΔDeviation(1 mil)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Fill table with saved solutions
        self.refresh_table()

        # Delete button
        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_selected)

        self.layout.addWidget(self.table)
        self.layout.addWidget(self.delete_button)

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

            # Update the parent's saved solutions
            self.parent_window.save_solutions_to_file()
            self.refresh_table()

    def closeEvent(self, event):
        if hasattr(self.parent_window, 'saved_solutions_dialog'):
            self.parent_window.saved_solutions_dialog = None
        event.accept()