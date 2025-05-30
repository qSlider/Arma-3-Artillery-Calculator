import os

from PyQt5.QtWidgets import (
    QMainWindow, QGraphicsView, QGraphicsScene, QVBoxLayout, QWidget, QComboBox, QLabel, QPushButton, QHBoxLayout,
    QMessageBox, QLineEdit, QGraphicsItem
)
from PyQt5.QtGui import QPixmap, QPainter, QBrush, QCursor
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import QGraphicsEllipseItem
from logic.heightsLogic import get_height_for_coordinates
from PyQt5.QtSvg import QGraphicsSvgItem


class MapView(QGraphicsView):
    point_added = pyqtSignal(str, float, float)

    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing, False)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)  # Добавлено
        self.setOptimizationFlag(QGraphicsView.DontAdjustForAntialiasing)  # Добавлено
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
        if self.scale_factor > 5.0 and event.angleDelta().y() > 0:
            event.ignore()
            return
        super().wheelEvent(event)
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

    def drawBackground(self, painter, rect):
        zoom_level = self.transform().m11()

        if zoom_level < 0.5:
            # Грубый рендеринг для мелкого масштаба
            painter.setRenderHint(QPainter.Antialiasing, False)
        else:
            # Детальный рендеринг
            painter.setRenderHint(QPainter.Antialiasing, True)

class OptimizedSVGItem(QGraphicsSvgItem):
    def __init__(self, path):
        super().__init__(path)
        self.setFlags(QGraphicsItem.ItemClipsToShape)
        self.setCacheMode(QGraphicsItem.NoCache)  # Временно отключите кэш

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        super().paint(painter, option, widget)

class MapWindow(QMainWindow):
    coordinates_selected = pyqtSignal(tuple, tuple, float, float)

    def __init__(self):
        super().__init__()
        self.current_map_height = 0  # Переименовано для общей логики
        self.current_map_item = None  # Для хранения текущего элемента карты
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

        if not os.path.exists(self.map_dir):
            print(f"Directory {self.map_dir} does not exist!")
        else:
            print(f"Maps will be loaded from {self.map_dir}")

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
            print(f"Directory {self.map_dir} does not exist!")
            return

        # Добавляем фильтр для .svg файлов
        map_files = [f for f in os.listdir(self.map_dir) if f.lower().endswith(('.png', '.jpg', '.svg'))]

        if map_files:
            print(f"Found the following map files: {map_files}")
        else:
            print("No map files found in the directory!")

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
        else:
            self.display_error("Map file does not exist.")

    def display_raster(self, path):
        """Отображение растровых изображений (PNG, JPG)"""
        pixmap = QPixmap(path)
        if pixmap.isNull():
            self.display_error("Failed to load raster image.")
            return

        self.scene.clear()
        self.current_map_item = self.scene.addPixmap(pixmap)
        self.current_map_height = pixmap.height()
        self.reset_and_fit()

    def display_svg(self, path):
        """Отображение SVG изображений"""
        try:
            svg_item = OptimizedSVGItem(path)
            if not svg_item.renderer().isValid():
                raise Exception("Invalid SVG renderer")

            print(f"SVG size: {svg_item.boundingRect().size()}")  # Debug output

            self.scene.clear()
            self.current_map_item = svg_item
            self.scene.addItem(svg_item)

            # Определение размеров
            viewbox = svg_item.renderer().viewBox()
            if viewbox.isEmpty():
                self.current_map_height = svg_item.boundingRect().height()
            else:
                self.current_map_height = viewbox.height()

            print(f"Map height: {self.current_map_height}")  # Debug output

            # Принудительное обновление
            self.scene.update()
            self.reset_and_fit()

        except Exception as e:
            self.display_error(f"SVG Error: {str(e)}")

    def reset_and_fit(self):
        if self.current_map_item:
            print(f"Fitting to: {self.current_map_item.boundingRect()}")  # Debug
            QTimer.singleShot(150, lambda: self.map_view.fitInView(
                self.current_map_item.boundingRect(),
                Qt.KeepAspectRatio
            ))

    def reset_zoom(self):
        self.map_view.resetTransform()
        self.map_view.scale_factor = 1.0

    def display_map(self, pixmap):
        self.scene.clear()
        self.reset_zoom()
        self.scene.addPixmap(pixmap)
        self.map_view.setScene(self.scene)
        self.scene.update()
        self.current_pixmap_height = pixmap.height()  # Сохраняем высоту карты
        QTimer.singleShot(150, lambda: self.map_view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio))

    def handle_point_added(self, point_type, x, y):
        corrected_y = self.current_map_height - y
        map_name = os.path.splitext(self.map_selector.currentText())[0]
        height_file = os.path.join(self.data_dir, f"{map_name}.txt")

        if not os.path.exists(height_file):
            print(f"Height file {height_file} not found!")
            return

        height = get_height_for_coordinates(x, corrected_y, height_file)

        if point_type == "Artillery":
            self.artillery_coords = (x, corrected_y)
            self.artillery_height = height
        elif point_type == "Target":
            self.target_coords = (x, corrected_y)
            self.target_height = height

        if self.artillery_coords and self.target_coords:
            self.coordinates_selected.emit(
                self.artillery_coords,
                self.target_coords,
                self.artillery_height,
                self.target_height
            )

            self.artillery_coords = None
            self.target_coords = None

    def emit_coordinates(self, x, y):
        self.coordinates_selected.emit({'x': x, 'y': y})

    def get_coordinates(self):
        return {'x': 100, 'y': 200}
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")

        self.map_window_button = QPushButton("Open Map")
        self.map_window_button.clicked.connect(self.open_map_window)

        self.artillery_x = QLineEdit()
        self.artillery_x.setPlaceholderText("Artillery X")

        self.artillery_y = QLineEdit()
        self.artillery_y.setPlaceholderText("Artillery Y")

        self.target_x = QLineEdit()
        self.target_x.setPlaceholderText("Target X")

        self.target_y = QLineEdit()
        self.target_y.setPlaceholderText("Target Y")

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
            self.map_window.coordinates_selected.connect(self.update_coordinates)
        self.map_window.show()

    def update_coordinates(self, artillery_coords, target_coords):
        self.artillery_x.setText(f"{artillery_coords[0]:.2f}")
        self.artillery_y.setText(f"{artillery_coords[1]:.2f}")
        self.target_x.setText(f"{target_coords[0]:.2f}")
        self.target_y.setText(f"{target_coords[1]:.2f}")



if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())