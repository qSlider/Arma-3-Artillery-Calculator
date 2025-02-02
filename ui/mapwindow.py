import os
os.environ["QT_OPENGL"] = "angle"  # Используйте "software", если хотите отключить OpenGL

from PyQt5.QtWidgets import (
    QMainWindow, QGraphicsView, QGraphicsScene, QVBoxLayout, QWidget, QComboBox, QLabel, QMessageBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(message)s")
logging.debug("Message here")

class MapLoaderThread(QThread):
    map_loaded = pyqtSignal(QPixmap)
    error = pyqtSignal(str)

    def __init__(self, map_path):
        super().__init__()
        self.map_path = map_path

    def run(self):
        if os.path.exists(self.map_path):
            pixmap = QPixmap(self.map_path)
            if not pixmap.isNull():
                self.map_loaded.emit(pixmap)
            else:
                self.error.emit("Failed to load map: invalid file.")
        else:
            self.error.emit("Map file does not exist.")


class MapView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.SmoothPixmapTransform)  # Улучшение качества рендера
        self.scale_factor = 1.0
        self.min_scale = 0.1  # Минимальный масштаб
        self.max_scale = 10.0  # Максимальный масштаб


    def wheelEvent(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 0.8

        if event.angleDelta().y() > 0:  # Прокрутка вверх
            zoom_factor = zoom_in_factor
        else:  # Прокрутка вниз
            zoom_factor = zoom_out_factor

        # Рассчёт нового масштаба
        new_scale = self.scale_factor * zoom_factor
        if self.min_scale <= new_scale <= self.max_scale:
            self.scale(zoom_factor, zoom_factor)
            self.scale_factor = new_scale
        else:
            event.ignore()


class MapWindow(QMainWindow):
    def __init__(self, map_dir="map/img"):
        super().__init__()
        self.setWindowTitle("Map Viewer")
        self.resize(800, 600)

        # UI элементы
        self.map_label = QLabel("Select Map:")
        self.map_selector = QComboBox()
        self.map_selector.currentIndexChanged.connect(self.load_map)

        # Графическая сцена и виджет
        self.scene = QGraphicsScene()
        self.map_view = MapView(self.scene)

        # Директория с картами
        self.map_dir = map_dir
        self.load_map_files()

        # Основной макет
        layout = QVBoxLayout()
        layout.addWidget(self.map_label)
        layout.addWidget(self.map_selector)
        layout.addWidget(self.map_view)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Загрузка первой карты, если она доступна
        if self.map_selector.count() > 0:
            self.load_map(0)

        # Переменная для потока
        self.loader_thread = None

    def load_map_files(self):
        """Загружает список карт из директории."""
        if not os.path.exists(self.map_dir):
            os.makedirs(self.map_dir)

        map_files = [f for f in os.listdir(self.map_dir) if f.endswith(".png")]
        if map_files:
            self.map_selector.addItems(map_files)
        else:
            self.map_selector.addItem("No maps available")

    def load_map(self, index):
        """Загружает карту без потока."""
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

    def display_map(self, pixmap):
        """Отображает загруженную карту."""
        self.scene.clear()
        self.scene.addPixmap(pixmap)
        self.map_view.setScene(self.scene)
        self.map_view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)

    def display_error(self, message):
        """Отображает сообщение об ошибке."""
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
