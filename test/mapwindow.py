import os

from PyQt5.QtWidgets import (
    QMainWindow, QGraphicsView, QGraphicsScene, QVBoxLayout, QWidget, QComboBox, QLabel, QPushButton, QHBoxLayout,
    QMessageBox, QLineEdit
)
from PyQt5.QtGui import QPixmap, QPainter, QBrush, QCursor
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import QGraphicsEllipseItem
from logic.heightsLogic import get_height_for_coordinates
from PyQt5.QtSvg import QGraphicsSvgItem, QSvgRenderer

def svg_map_loader(map_dir, map_files):
    for map_file in map_files:
        map_path = os.path.join(map_dir, map_file)
        yield map_path

class MapView(QGraphicsView):
    point_added = pyqtSignal(str, float, float)

    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setRenderHint(QPainter.Antialiasing)
        self.scale_factor = 1.0
        self.min_scale = 0.1
        self.max_scale = 30.0
        self.dragging = False
        self.last_mouse_position = None
        self.current_markers = {}
        self.selected_point_type = None

    def wheelEvent(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 0.8
        zoom_factor = zoom_in_factor if event.angleDelta().y() > 0 else zoom_out_factor
        new_scale = self.scale_factor * zoom_factor
        if self.min_scale <= new_scale <= self.max_scale:
            self.scale(zoom_factor, zoom_factor)
            self.scale_factor = new_scale
        else:
            event.ignore()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.selected_point_type:
                self.add_point(self.selected_point_type)
                self.selected_point_type = None
            else:
                self.dragging = True
                self.last_mouse_position = event.pos()
                self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging:
            delta = event.pos() - self.last_mouse_position
            self.last_mouse_position = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(event)

    def add_point(self, point_type):
        color = Qt.blue if point_type == "Artillery" else Qt.red
        mouse_pos = self.mapToScene(self.mapFromGlobal(QCursor.pos()))
        x, y = mouse_pos.x(), mouse_pos.y()

        if point_type in self.current_markers:
            self.scene().removeItem(self.current_markers[point_type])

        circle = QGraphicsEllipseItem(-5, -5, 10, 10)
        circle.setBrush(QBrush(color))
        circle.setPos(x, y)
        self.scene().addItem(circle)

        self.current_markers[point_type] = circle
        self.point_added.emit(point_type, x, y)

class MapWindow(QMainWindow):
    artillery_coordinates_selected = pyqtSignal(tuple, float)
    target_coordinates_selected = pyqtSignal(tuple, float)

    def __init__(self):
        super().__init__()
        self.current_map_height = 0
        self.current_map_item = None
        self.current_pixmap_height = 0
        self.setWindowTitle("Map Viewer")
        self.resize(800, 600)

        self.map_label = QLabel("Select Map:")
        self.map_selector = QComboBox()
        self.map_selector.currentIndexChanged.connect(self.load_map)

        self.scene = QGraphicsScene()
        self.map_view = MapView(self.scene)
        self.map_view.point_added.connect(self.handle_point_added)

        self.artillery_button = QPushButton("Add Artillery")
        self.artillery_button.clicked.connect(lambda: self.select_point("Artillery"))

        self.target_button = QPushButton("Add Target")
        self.target_button.clicked.connect(lambda: self.select_point("Target"))

        self.map_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'map', 'img')
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'map', 'data')

        self.load_map_files()

        layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.artillery_button)
        button_layout.addWidget(self.target_button)

        layout.addWidget(self.map_label)
        layout.addWidget(self.map_selector)
        layout.addLayout(button_layout)
        layout.addWidget(self.map_view)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        if self.map_selector.count() > 0:
            self.load_map(0)

        self.artillery_coords = None
        self.target_coords = None

    def select_point(self, point_type):
        self.map_view.selected_point_type = point_type

    def load_map_files(self):
        if not os.path.exists(self.map_dir):
            return

        map_files = [f for f in os.listdir(self.map_dir) if f.lower().endswith(('.png', '.jpg', '.svg'))]
        self.map_selector.addItems(map_files)

    def load_map(self, index):
        if index < 0 or self.map_selector.count() == 0:
            return

        map_name = self.map_selector.currentText()
        map_path = os.path.join(self.map_dir, map_name)
        ext = os.path.splitext(map_name)[1].lower()

        if os.path.exists(map_path):
            if ext == '.svg':
                self.display_svg(map_path)
            else:
                self.display_raster(map_path)

    def display_raster(self, path):
        pixmap = QPixmap(path)
        if pixmap.isNull():
            return

        self.scene.clear()
        self.current_map_item = self.scene.addPixmap(pixmap)
        self.current_map_height = pixmap.height()
        self.reset_and_fit()

    def display_svg(self, path):
        svg_item = QGraphicsSvgItem(path)
        renderer = svg_item.renderer()
        if not renderer or not renderer.isValid():
            return

        self.scene.clear()
        self.current_map_item = svg_item
        self.scene.addItem(svg_item)

        viewbox = renderer.viewBoxF()
        self.current_map_height = viewbox.height() if not viewbox.isEmpty() else 0
        self.reset_and_fit()

    def reset_and_fit(self):
        self.reset_zoom()
        if self.current_map_item:
            QTimer.singleShot(150, lambda: self.map_view.fitInView(
                self.current_map_item.boundingRect(), Qt.KeepAspectRatio))

    def reset_zoom(self):
        self.map_view.resetTransform()
        self.map_view.scale_factor = 1.0

    def handle_point_added(self, point_type, x, y):
        corrected_y = self.current_map_height - y
        map_name = os.path.splitext(self.map_selector.currentText())[0]
        height_file = os.path.join(self.data_dir, f"{map_name}.txt")

        if not os.path.exists(height_file):
            return

        height = get_height_for_coordinates(x, corrected_y, height_file)

        if point_type == "Artillery":
            self.artillery_coords = (x, corrected_y)
            self.artillery_height = height
            self.artillery_coordinates_selected.emit(self.artillery_coords, self.artillery_height)

        elif point_type == "Target":
            self.target_coords = (x, corrected_y)
            self.target_height = height
            self.target_coordinates_selected.emit(self.target_coords, self.target_height)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")

        self.map_window_button = QPushButton("Open Map")
        self.map_window_button.clicked.connect(self.open_map_window)

        self.artillery_x = QLineEdit()
        self.artillery_y = QLineEdit()
        self.target_x = QLineEdit()
        self.target_y = QLineEdit()

        layout = QVBoxLayout()
        layout.addWidget(self.map_window_button)
        layout.addWidget(QLabel("Artillery Coordinates:"))
        layout.addWidget(self.artillery_x)
        layout.addWidget(self.artillery_y)
        layout.addWidget(QLabel("Target Coordinates:"))
        layout.addWidget(self.target_x)
        layout.addWidget(self.target_y)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.map_window = None

    def open_map_window(self):
        if not self.map_window:
            self.map_window = MapWindow()
            self.map_window.artillery_coordinates_selected.connect(self.update_artillery_coordinates)
            self.map_window.target_coordinates_selected.connect(self.update_target_coordinates)
        self.map_window.show()

    def update_artillery_coordinates(self, artillery_coords, _):
        self.artillery_x.setText(f"{artillery_coords[0]:.2f}")
        self.artillery_y.setText(f"{artillery_coords[1]:.2f}")

    def update_target_coordinates(self, target_coords, _):
        self.target_x.setText(f"{target_coords[0]:.2f}")
        self.target_y.setText(f"{target_coords[1]:.2f}")

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())