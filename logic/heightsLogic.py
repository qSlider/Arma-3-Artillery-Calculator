import math


# Чтение данных из файла
def read_data(file_path):
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            parts = line.split()
            x = float(parts[0])
            y = float(parts[1])
            height = float(parts[2])
            data.append((x, y, height))
    return data


# Функция для нахождения ближайшей точки
def find_nearest_point(x, y, data):
    nearest_point = None
    min_distance = float('inf')

    for (data_x, data_y, height) in data:
        distance = math.sqrt((data_x - x) ** 2 + (data_y - y) ** 2)
        if distance < min_distance:
            min_distance = distance
            nearest_point = (data_x, data_y, height)

    return nearest_point


# Основная логика
def get_height_for_coordinates(x, y, file_path):
    data = read_data(file_path)
    nearest_point = find_nearest_point(x, y, data)

    if nearest_point:
        return nearest_point[2]  # Возвращаем высоту ближайшей точки
    else:
        return None


# Пример использования
file_path = r'C:\Users\mstre\PycharmProjects\ArtilleryCalcu\map\data\virolahti.txt'  # Путь к файлу
x_input = 14851  # Пример введенных координат X
y_input = 15100  # Пример введенных координат Y

height = get_height_for_coordinates(x_input, y_input, file_path)
if height is not None:
    print(f"Высота для координат ({x_input}, {y_input}) составляет {height}")
else:
    print("Не удалось найти ближайшую точку.")
