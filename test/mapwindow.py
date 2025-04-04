import os
import math
from PyQt5.QtWidgets import (
    QMainWindow, QGraphicsView, QGraphicsScene, QVBoxLayout, QWidget, QComboBox, QLabel, QPushButton, QHBoxLayout,
    QMessageBox, QLineEdit, QGraphicsItem, QGraphicsRectItem
)
from PyQt5.QtGui import QPixmap, QPainter, QBrush, QCursor, QTransform, QColor
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QRectF, QPointF
from PyQt5.QtWidgets import QGraphicsEllipseItem
from logic.heightsLogic import get_height_for_coordinates
from PyQt5.QtSvg import QGraphicsSvgItem, QSvgRenderer


class SvgTile(QGraphicsSvgItem):
    """Custom SVG tile class to handle parts of a larger SVG"""

    def __init__(self, file_path, viewbox_rect):
        super().__init__()
        self.file_path = file_path
        self.viewbox_rect = viewbox_rect

        # Create renderer with clipping viewport
        self.custom_renderer = QSvgRenderer(file_path)
        self.custom_renderer.setViewBox(viewbox_rect)
        self.setSharedRenderer(self.custom_renderer)

        # Position the tile at its correct position in the overall map
        self.setPos(viewbox_rect.x(), viewbox_rect.y())


class TiledMapView(QGraphicsView):
    point_added = pyqtSignal(str, float, float)

    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setRenderHint(QPainter.Antialiasing)

        # Scale factors and limits
        self.scale_factor = 1.0
        self.min_scale = 0.01  # Lower min scale for large maps
        self.max_scale = 30.0

        # Mouse interaction vars
        self.dragging = False
        self.last_mouse_position = None
        self.current_markers = {}
        self.selected_point_type = None

        # Tile management
        self.tile_size = 1000  # Size of each tile in SVG units
        self.loaded_tiles = {}  # Keep track of loaded tiles
        self.full_svg_size = (0, 0)  # Will be set when loading map
        self.svg_path = None
        self.visible_tiles = set()

        # Set less frequent tile updates to avoid stack overflow
        self.tile_load_timer = QTimer(self)
        self.tile_load_timer.setSingleShot(True)
        self.tile_load_timer.timeout.connect(self.update_visible_tiles)

        # Viewport change tracking
        self.viewport_update_pending = False

        # For PNG/JPG maps
        self.using_raster_map = False
        self.raster_map_item = None

    def resizeEvent(self, event):
        """Handle resize events to update tiles"""
        super().resizeEvent(event)
        self.schedule_tile_update()

    def schedule_tile_update(self):
        """Schedule a tile update with a delay to avoid too many updates"""
        if not self.viewport_update_pending and not self.using_raster_map:
            self.viewport_update_pending = True
            self.tile_load_timer.start(200)  # 200ms delay

    def load_svg_map(self, svg_path):
        """Load a SVG map and prepare it for tiled rendering"""
        self.svg_path = svg_path
        self.loaded_tiles.clear()
        self.scene().clear()
        self.using_raster_map = False

        # Get the full size of the SVG
        temp_renderer = QSvgRenderer(svg_path)
        if not temp_renderer.isValid():
            print(f"Error: Unable to load SVG {svg_path}")
            return False

        viewbox = temp_renderer.viewBox()
        self.full_svg_size = (viewbox.width(), viewbox.height())
        print(f"Full SVG size: {self.full_svg_size}")

        # Create a placeholder rectangle to define the scene bounds
        placeholder = QGraphicsRectItem(0, 0, self.full_svg_size[0], self.full_svg_size[1])
        placeholder.setPen(Qt.NoPen)
        placeholder.setBrush(Qt.NoBrush)
        self.scene().addItem(placeholder)

        # Set the proper bounding rect for the scene
        self.scene().setSceneRect(0, 0, self.full_svg_size[0], self.full_svg_size[1])

        # Initial tiles load for the current viewport
        self.schedule_tile_update()
        return True

    def load_raster_map(self, pixmap_path):
        """Load a regular PNG/JPG map"""
        self.using_raster_map = True
        self.svg_path = None
        self.loaded_tiles.clear()
        self.scene().clear()

        # Stop tile timer if running
        self.tile_load_timer.stop()
        self.viewport_update_pending = False

        # Load the pixmap
        pixmap = QPixmap(pixmap_path)
        if pixmap.isNull():
            return False

        # Add to scene
        self.raster_map_item = self.scene().addPixmap(pixmap)
        self.scene().setSceneRect(pixmap.rect())

        return True

    def update_visible_tiles(self):
        """Update which tiles are visible and load/unload as needed"""
        self.viewport_update_pending = False

        if not self.svg_path or self.using_raster_map:
            return

        # Get the current viewport in scene coordinates
        viewport_rect = self.mapToScene(self.viewport().rect()).boundingRect()

        # Add a safety margin for smoother scrolling
        margin = self.tile_size
        viewport_rect = viewport_rect.adjusted(-margin, -margin, margin, margin)

        # Calculate which tiles intersect with the viewport
        start_x = max(0, math.floor(viewport_rect.left() / self.tile_size))
        start_y = max(0, math.floor(viewport_rect.top() / self.tile_size))
        end_x = min(math.ceil(self.full_svg_size[0] / self.tile_size),
                    math.ceil(viewport_rect.right() / self.tile_size))
        end_y = min(math.ceil(self.full_svg_size[1] / self.tile_size),
                    math.ceil(viewport_rect.bottom() / self.tile_size))

        # Set a limit on how many tiles to load at once to prevent stack overflow
        max_tiles_to_load = 25  # Adjust based on your system capabilities

        # Calculate visible tiles
        new_visible_tiles = set()
        tiles_loaded_this_batch = 0

        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                tile_key = (x, y)
                new_visible_tiles.add(tile_key)

                # Load any tiles not already loaded, up to the limit
                if tile_key not in self.loaded_tiles and tiles_loaded_this_batch < max_tiles_to_load:
                    self.load_tile(x, y)
                    tiles_loaded_this_batch += 1

        # If we hit the limit, schedule another update soon
        if tiles_loaded_this_batch >= max_tiles_to_load:
            self.schedule_tile_update()
            return

        # Remove tiles that are no longer visible (with some buffer to reduce frequent load/unload)
        tiles_to_remove = set()
        for tile_key in self.loaded_tiles.keys():
            if tile_key not in new_visible_tiles:
                # Keep a buffer of tiles around the viewport
                tx, ty = tile_key
                if (tx < start_x - 2 or tx > end_x + 2 or
                        ty < start_y - 2 or ty > end_y + 2):
                    tiles_to_remove.add(tile_key)

        for tile_key in tiles_to_remove:
            if tile_key in self.loaded_tiles:
                tile_item = self.loaded_tiles[tile_key]
                if tile_item in self.scene().items():
                    self.scene().removeItem(tile_item)
                del self.loaded_tiles[tile_key]

        self.visible_tiles = new_visible_tiles

    def load_tile(self, tile_x, tile_y):
        """Load a specific tile from the SVG"""
        # Skip if outside bounds
        if (tile_x < 0 or tile_y < 0 or
                tile_x * self.tile_size >= self.full_svg_size[0] or
                tile_y * self.tile_size >= self.full_svg_size[1]):
            return

        # Calculate tile boundaries in SVG coordinates
        x_start = tile_x * self.tile_size
        y_start = tile_y * self.tile_size
        width = min(self.tile_size, self.full_svg_size[0] - x_start)
        height = min(self.tile_size, self.full_svg_size[1] - y_start)

        # Create the viewbox for this tile
        viewbox = QRectF(x_start, y_start, width, height)

        try:
            # Create the tile
            tile = SvgTile(self.svg_path, viewbox)

            # Add to scene and track it
            self.scene().addItem(tile)
            self.loaded_tiles[(tile_x, tile_y)] = tile
        except Exception as e:
            print(f"Error loading tile ({tile_x}, {tile_y}): {e}")

    def wheelEvent(self, event):
        # Store the scene position where the mouse is
        old_pos = self.mapToScene(event.pos())

        # Calculate zoom factor
        zoom_in_factor = 1.2
        zoom_out_factor = 1.0 / zoom_in_factor
        zoom_factor = zoom_in_factor if event.angleDelta().y() > 0 else zoom_out_factor

        # Apply zoom limits
        new_scale = self.scale_factor * zoom_factor
        if self.min_scale <= new_scale <= self.max_scale:
            self.scale_factor = new_scale
            self.scale(zoom_factor, zoom_factor)

            # Adjust viewport to keep mouse position stable
            new_pos = self.mapToScene(event.pos())
            delta = new_pos - old_pos
            self.translate(delta.x(), delta.y())

            # Schedule tile update
            self.schedule_tile_update()
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

            # Update scrollbars
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())

            # Schedule tile update
            self.schedule_tile_update()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.setCursor(Qt.ArrowCursor)

            # Make sure tiles are updated after dragging stops
            if not self.using_raster_map:
                self.schedule_tile_update()
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
        circle.setZValue(1000)  # Ensure the marker is displayed on top of tiles
        self.scene().addItem(circle)

        self.current_markers[point_type] = circle
        self.point_added.emit(point_type, x, y)


class MapWindow(QMainWindow):
    artillery_coordinates_selected = pyqtSignal(tuple, float)
    target_coordinates_selected = pyqtSignal(tuple, float)

    def __init__(self):
        super().__init__()
        self.current_map_height = 0
        self.setWindowTitle("Tiled Map Viewer")
        self.resize(1000, 800)

        self.map_label = QLabel("Select Map:")
        self.map_selector = QComboBox()
        self.map_selector.currentIndexChanged.connect(self.load_map)

        self.scene = QGraphicsScene()
        # Use our tiled map view
        self.map_view = TiledMapView(self.scene)
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

        # Status label for debugging
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

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

        map_files = [f for f in os.listdir(self.map_dir) if f.lower().endswith(('.png', '.jpg', '.svg'))]

        if map_files:
            print(f"Found the following map files: {map_files}")
        else:
            print("No map files found in the directory!")

        self.map_selector.addItems(map_files)

    def load_map(self, index):
        if index < 0 or self.map_selector.count() == 0:
            return

        try:
            map_name = self.map_selector.currentText()
            map_path = os.path.join(self.map_dir, map_name)
            ext = os.path.splitext(map_name)[1].lower()

            if os.path.exists(map_path):
                self.status_label.setText(f"Loading {map_name}...")
                QApplication.processEvents()  # Update UI

                if ext == '.svg':
                    self.display_svg_tiled(map_path)
                else:
                    self.display_raster(map_path)

                self.status_label.setText(f"Loaded {map_name}")
            else:
                self.display_error("Map file does not exist.")
        except Exception as e:
            self.display_error(f"Error loading map: {str(e)}")
            print(f"Error details: {e}")

    def display_svg_tiled(self, path):
        """Display SVG using the tiled approach"""
        # Clear the scene and reset the view
        self.map_view.resetTransform()

        # Get the SVG's full dimensions for reference
        temp_renderer = QSvgRenderer(path)
        if not temp_renderer.isValid():
            self.display_error("Failed to load SVG image.")
            return

        viewbox = temp_renderer.viewBox()
        self.current_map_height = viewbox.height()

        # Load the tiled SVG
        success = self.map_view.load_svg_map(path)
        if not success:
            self.display_error("Failed to prepare tiled SVG map.")
            return

        # Fit the map in view
        self.fitMapInView()

    def display_raster(self, path):
        """Display regular raster images"""
        # Stop the tile-based rendering and use regular pixmap
        success = self.map_view.load_raster_map(path)
        if not success:
            self.display_error("Failed to load raster image.")
            return

        # Get pixmap height for coordinate conversion
        pixmap = QPixmap(path)
        self.current_map_height = pixmap.height()

        # Fit in view
        self.fitMapInView()

    def fitMapInView(self):
        """Adjust view to fit the map"""
        self.map_view.resetTransform()
        self.map_view.scale_factor = 1.0

        # Fit to scene rect
        QTimer.singleShot(100, lambda: self.map_view.fitInView(
            self.scene.sceneRect(),
            Qt.KeepAspectRatio
        ))

    def display_error(self, message):
        self.status_label.setText(f"Error: {message}")
        QMessageBox.critical(self, "Error", message)

    def handle_point_added(self, point_type, x, y):
        try:
            corrected_y = self.current_map_height - y
            map_name = os.path.splitext(self.map_selector.currentText())[0]
            height_file = os.path.join(self.data_dir, f"{map_name}.txt")

            if not os.path.exists(height_file):
                print(f"Height file {height_file} not found!")
                height = 0
            else:
                height = get_height_for_coordinates(x, corrected_y, height_file)

            if point_type == "Artillery":
                self.artillery_coords = (x, corrected_y)
                self.artillery_height = height
                self.artillery_coordinates_selected.emit(self.artillery_coords, self.artillery_height)
                self.status_label.setText(f"Artillery set at ({x:.1f}, {corrected_y:.1f}), height: {height}")

            elif point_type == "Target":
                self.target_coords = (x, corrected_y)
                self.target_height = height
                self.target_coordinates_selected.emit(self.target_coords, self.target_height)
                self.status_label.setText(f"Target set at ({x:.1f}, {corrected_y:.1f}), height: {height}")

        except Exception as e:
            self.status_label.setText(f"Error adding point: {str(e)}")
            print(f"Point addition error: {e}")


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
            self.map_window.artillery_coordinates_selected.connect(self.update_artillery_coordinates)
            self.map_window.target_coordinates_selected.connect(self.update_target_coordinates)
        self.map_window.show()

    def update_artillery_coordinates(self, artillery_coords, height):
        self.artillery_x.setText(f"{artillery_coords[0]:.2f}")
        self.artillery_y.setText(f"{artillery_coords[1]:.2f}")

    def update_target_coordinates(self, target_coords, height):
        self.target_x.setText(f"{target_coords[0]:.2f}")
        self.target_y.setText(f"{target_coords[1]:.2f}")


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())