import os
os.environ["QT_OPENGL"] = "desktop"  # Пробуйте "software" или "desktop" в зависимости от системы

from PyQt5.QtWidgets import (
    QMainWindow, QGraphicsView, QGraphicsScene, QVBoxLayout, QWidget, QComboBox, QLabel, QMessageBox,
    QGraphicsEllipseItem
)
from PyQt5.QtGui import QPixmap, QPainter, QBrush, QCursor
from PyQt5.QtCore import Qt, QTimer, pyqtSignal


class MapView(QGraphicsView):
    point_added = pyqtSignal(str, float, float)

    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setRenderHint(QPainter.Antialiasing)
        self.scale_factor = 1.0
        self.min_scale = 0.1
        self.max_scale = 25.0
        self.dragging = False
        self.last_mouse_position = None
        self.map_width = 10000
        self.map_height = 10000

        # Словарь для хранения текущих меток
        self.current_markers = {}

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

    def set_map_size(self, width, height):
        """Метод для изменения размеров карты."""
        self.map_width = width
        self.map_height = height
        self.scene().setSceneRect(0, 0, width, height)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_BracketLeft:  # Кнопка [
            self.add_point("Artillery", Qt.blue)  # Синий кружок
        elif event.key() == Qt.Key_BracketRight:  # Кнопка ]
            self.add_point("Target", Qt.red)  # Красный кружок
        elif event.key() == Qt.Key_Delete:  # Кнопка Delete
            self.clear_all_points()
        super().keyPressEvent(event)

    def add_point(self, point_type, color):
        # Получаем координаты мыши относительно сцены
        mouse_pos = self.mapToScene(self.mapFromGlobal(QCursor.pos()))
        x = mouse_pos.x()
        y = mouse_pos.y()

        # Преобразуем в систему координат карты с учетом масштаба
        map_x = (x / self.sceneRect().width()) * self.map_width
        map_y = (y / self.sceneRect().height()) * self.map_height

        # Если точка такого типа уже существует, удаляем её
        if point_type in self.current_markers:
            self.scene().removeItem(self.current_markers[point_type])

        # Создаем новую точку (кружок)
        circle = QGraphicsEllipseItem(-5, -5, 10, 10)  # Радиус 5
        circle.setBrush(QBrush(color))
        circle.setPos(x, y)  # Устанавливаем позицию кружка
        self.scene().addItem(circle)

        # Обновляем текущую метку
        self.current_markers[point_type] = circle

        # Передаем новые координаты в MainWindow
        self.point_added.emit(point_type, map_x, map_y)

    def clear_all_points(self):
        """Удаляет все метки с карты."""
        for marker in self.current_markers.values():
            self.scene().removeItem(marker)
        self.current_markers.clear()


class MapWindow(QMainWindow):
    def __init__(self, map_dir="map/img"):
        super().__init__()
        self.setWindowTitle("Map Viewer")
        self.resize(800, 600)

        self.map_label = QLabel("Select Map:")
        self.map_selector = QComboBox()
        self.map_selector.currentIndexChanged.connect(self.load_map)

        self.scene = QGraphicsScene()
        self.map_view = MapView(self.scene)
        self.map_view.point_added.connect(self.handle_point_added)

        self.map_dir = map_dir
        self.load_map_files()

        layout = QVBoxLayout()
        layout.addWidget(self.map_label)
        layout.addWidget(self.map_selector)
        layout.addWidget(self.map_view)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        if self.map_selector.count() > 0:
            self.load_map(0)

    def load_map_files(self):
        if not os.path.exists(self.map_dir):
            os.makedirs(self.map_dir)

        map_files = [f for f in os.listdir(self.map_dir) if f.endswith(".png")]
        if map_files:
            self.map_selector.addItems(map_files)
        else:
            self.map_selector.addItem("No maps available")

    def load_map(self, index):
        if index < 0 or self.map_selector.count() == 0:
            return

        map_name = self.map_selector.currentText()
        map_path = os.path.join(self.map_dir, map_name)

        if os.path.exists(map_path):
            pixmap = QPixmap(map_path)
            if not pixmap.isNull():
                self.display_map(pixmap)
            else:
                self.display_error("Failed to load map: invalid file.")
        else:
            self.display_error("Map file does not exist.")

    def reset_zoom(self):
        self.map_view.resetTransform()
        self.map_view.scale_factor = 1.0

    def display_map(self, pixmap):
        self.scene.clear()
        self.reset_zoom()
        self.scene.addPixmap(pixmap)
        self.map_view.setScene(self.scene)
        self.scene.update()
        QTimer.singleShot(150, lambda: self.map_view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio))

    def display_error(self, message):
        QMessageBox.critical(self, "Error", message)
        self.scene.clear()
        self.scene.addText("Error: " + message)

    def handle_point_added(self, point_type, x, y):
        print(f"{point_type} point added at ({x:.2f}, {y:.2f})")


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MapWindow()
    window.show()
    sys.exit(app.exec_())