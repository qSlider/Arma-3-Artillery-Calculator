import os
os.environ["QT_OPENGL"] = "angle"  # Пробуйте "software" или "desktop" в зависимости от системы

from PyQt5.QtWidgets import (
    QMainWindow, QGraphicsView, QGraphicsScene, QVBoxLayout, QWidget, QComboBox, QLabel, QMessageBox
)
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt, QTimer


class MapView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.SmoothPixmapTransform)  # Улучшение качества рендера
        self.setRenderHint(QPainter.Antialiasing)  # Устранение "рваных" краёв
        self.scale_factor = 1.0
        self.min_scale = 0.1
        self.max_scale = 25.0
        self.dragging = False
        self.last_mouse_position = None

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
        self.reset_zoom()  # Сброс масштаба перед загрузкой новой карты
        self.scene.addPixmap(pixmap)
        self.map_view.setScene(self.scene)
        self.scene.update()
        QTimer.singleShot(150, lambda: self.map_view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio))

    def display_error(self, message):
        QMessageBox.critical(self, "Error", message)
        self.scene.clear()
        self.scene.addText("Error: " + message)


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MapWindow()
    window.show()
    sys.exit(app.exec_())
