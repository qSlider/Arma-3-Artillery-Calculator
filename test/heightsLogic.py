import math
import numpy as np
from scipy.spatial import cKDTree


def read_data(file_path):
    """
    Чтение данных из файла с координатами и высотами.

    Args:
        file_path (str): Путь к файлу с данными

    Returns:
        tuple: Массивы координат и высот
    """
    data = np.loadtxt(file_path)
    return data[:, :2], data[:, 2]


def get_height_for_coordinates(x, y, file_path):
    """
    Быстрый поиск ближайшей высоты для заданных координат.

    Args:
        x (float): Координата x
        y (float): Координата y
        file_path (str): Путь к файлу с данными

    Returns:
        float: Высота для ближайшей точки
    """
    # Загрузка координат и высот
    coords, heights = read_data(file_path)

    # Построение KD-дерева
    tree = cKDTree(coords)

    # Поиск ближайшей точки
    distance, index = tree.query([x, y])

    return heights[index]

# Пример использования
height = get_height_for_coordinates(5000, 3000, file_path = "C:\\Users\\mstre\\PycharmProjects\\pythonProject6\\map\\datadata\\virolahti.txt")
print(height)