import math
from scipy.spatial import cKDTree

#Global variables for caching
_tree = None
_coords = None
_heights = None
_loaded_file = None


def read_data(file_path):
    global _tree, _coords, _heights, _loaded_file

    if _tree is not None and _loaded_file == file_path:
        return

    coords = []
    heights = []

    with open(file_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 3:
                continue
            try:
                x = float(parts[0])
                y = float(parts[1])
                h = float(parts[2])
                coords.append((x, y))
                heights.append(h)
            except ValueError:
                continue

    if coords:
        _tree = cKDTree(coords)
        _coords = coords
        _heights = heights
        _loaded_file = file_path


def find_nearest_point(x, y):
    global _tree, _heights
    if not _tree:
        return None
    distance, index = _tree.query((x, y))
    return _heights[index]


def get_height_for_coordinates(x, y, file_path):
    read_data(file_path)
    height = find_nearest_point(x, y)
    return height
