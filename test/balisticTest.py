import matplotlib
matplotlib.use('TkAgg')  # Используем стандартный backend
import matplotlib.pyplot as plt
import numpy as np

# Константы
g = 9.81  # Ускорение свободного падения, м/с²
k_base = 0.0001  # Базовый коэффициент сопротивления воздуха
rho_standard = 1.225  # Стандартная плотность воздуха на уровне моря, кг/м³

# Ветер (по желанию можно менять)
wind_x = 0  # Ветер по оси X
wind_y = 0  # Ветер по оси Y

# Ввод данных
v0 = float(input("Введите начальную скорость снаряда (м/с): "))
angle = float(input("Введите угол выстрела (градусы): "))
temperature = float(input("Введите температуру воздуха (°C): "))  # Новая переменная
rho = float(input("Введите плотность воздуха (кг/м³): "))  # Новая переменная

# Коррекция параметров
rho_ratio = rho / rho_standard  # Относительная плотность
k = k_base * rho_ratio  # Коррекция сопротивления
v0 *= np.sqrt((temperature + 273.15) / 288.15)  # Коррекция скорости

# Начальные условия
angle = np.radians(angle)  # Перевод угла в радианы
vx, vy, vz = v0 * np.cos(angle), 0, v0 * np.sin(angle)
x, y, z = 0, 0, 0  # Начальная позиция
dt = 0.01  # Малый шаг времени
trajectory = []

# Численное интегрирование методом Эйлера
while z >= 0:
    v = np.sqrt(vx**2 + vy**2 + vz**2)  # Модуль скорости
    dvx_dt = -k * vx * v + wind_x
    dvy_dt = -k * vy * v + wind_y
    dvz_dt = -g - k * vz * v

    vx += dvx_dt * dt
    vy += dvy_dt * dt
    vz += dvz_dt * dt

    x += vx * dt
    y += vy * dt
    z += vz * dt

    trajectory.append((x, z))

# Преобразуем в массив numpy для удобства
trajectory = np.array(trajectory)

# Построение графика
plt.figure(figsize=(10, 5))
plt.plot(trajectory[:, 0], trajectory[:, 1], label="Траектория снаряда")
plt.xlabel("Расстояние (м)")
plt.ylabel("Высота (м)")
plt.title("Траектория полёта снаряда с учётом атмосферы")
plt.legend()
plt.grid()
plt.show()
