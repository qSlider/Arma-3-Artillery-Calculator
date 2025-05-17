import os
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QLabel, QMessageBox, QProgressBar
)
from wand.image import Image


def create_folders():
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    folders = [
        os.path.join(base_dir, "map", "data"),
        os.path.join(base_dir, "map", "img")
    ]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    return os.path.join(base_dir, "map", "img")


class SVGConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SVG to PNG Converter")
        self.setGeometry(100, 100, 400, 200)

        self.layout = QVBoxLayout()
        self.label = QLabel("Select the SVG file to convert")
        self.layout.addWidget(self.label)

        self.select_button = QPushButton("Select file")
        self.select_button.clicked.connect(self.select_file)
        self.layout.addWidget(self.select_button)

        self.convert_button = QPushButton("Convert to PNG")
        self.convert_button.clicked.connect(self.convert_svg)
        self.convert_button.setEnabled(False)
        self.layout.addWidget(self.convert_button)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.layout.addWidget(self.progress)

        self.setLayout(self.layout)

        self.svg_path = None
        self.output_dir = create_folders()

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select SVG file", "", "SVG Files (*.svg)")
        if file_path:
            self.svg_path = file_path
            self.label.setText(f"File selected: {os.path.basename(file_path)}")
            self.convert_button.setEnabled(True)

    def convert_svg(self):
        if not self.svg_path:
            QMessageBox.warning(self, "Error", "First, select the SVG file.")
            return

        self.progress.setValue(25)

        try:
            with Image(filename=self.svg_path) as img:
                img.format = 'png'
                output_file = os.path.join(self.output_dir, os.path.splitext(os.path.basename(self.svg_path))[0] + ".png")
                img.save(filename=output_file)

            self.progress.setValue(100)
            QMessageBox.information(self, "Complete", f"The file has been successfully converted:\n{output_file}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"There was an error:\n{str(e)}")

        self.progress.setValue(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SVGConverter()
    window.show()
    sys.exit(app.exec_())
