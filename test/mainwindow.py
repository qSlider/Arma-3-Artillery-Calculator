import matplotlib
matplotlib.use('TkAgg')  # Используем стандартный backend
import matplotlib.pyplot as plt
import numpy as np

g = 9.81  # Ускорение свободного падения, м/с²
k_base = 6e-05  # Базовый коэффициент сопротивления воздуха
rho_standard = 1.225  # Стандартная плотность воздуха на уровне моря, кг/м³


def simulate_trajectory(v0, angle, k, target_distance, target_height, dt=0.01):
    """ Симуляция траектории снаряда """
    angle = np.radians(angle)
    vx, vz = v0 * np.cos(angle), v0 * np.sin(angle)
    x, z = 0, 0
    trajectory = []

    while z >= -target_height:  # Условие выхода
        v = np.sqrt(vx ** 2 + vz ** 2)
        dvx_dt = -k * vx * v
        dvz_dt = -g - k * vz * v

        vx += dvx_dt * dt
        vz += dvz_dt * dt
        x += vx * dt
        z += vz * dt

        trajectory.append((x, z))

        # Улучшенное сравнение с целью
        if abs(x - target_distance) < 1.0 and abs(z - target_height) < 1.0:
            return np.array(trajectory), True  # Снаряд достиг цели

    return np.array(trajectory), False


def find_optimal_angle(v0, target_distance, target_height, k, angle_step=0.1):
    best_angle = None
    min_error = float("inf")

    for angle in np.arange(0, 90, angle_step):
        trajectory, hit = simulate_trajectory(v0, angle, k, target_distance, target_height)
        for x, z in trajectory:
            if abs(x - target_distance) < 0.5 and abs(z - target_height) < 0.5:
                return angle  # Если нашли точку, где x ≈ target_distance и z ≈ target_height

    return None


# Ввод данных
v0 = float(input("Введите начальную скорость снаряда (м/с): "))
target_distance = float(input("Введите расстояние до цели (м): "))
target_height = float(input("Введите разницу высот (м, положительное - выше, отрицательное - ниже): "))
temperature = float(input("Введите температуру воздуха (°C): "))
rho = float(input("Введите плотность воздуха (кг/м³): "))

rho_ratio = rho / rho_standard  # Относительная плотность
k = k_base * rho_ratio  # Коррекция сопротивления
v0 *= np.sqrt((temperature + 273.15) / 288.15)  # Коррекция скорости

optimal_angle = find_optimal_angle(v0, target_distance, target_height, k)

if optimal_angle is not None:
    print(f"Оптимальный угол возвышения ствола: {optimal_angle:.2f} градусов")
    trajectory, _ = simulate_trajectory(v0, optimal_angle, k, target_distance, target_height)

    plt.figure(figsize=(10, 5))
    plt.plot(trajectory[:, 0], trajectory[:, 1], label=f"Траектория (угол {optimal_angle:.2f}°)")
    plt.axvline(target_distance, color='r', linestyle='--', label='Цель')
    plt.axhline(target_height, color='g', linestyle='--', label='Высота цели')
    plt.xlabel("Расстояние (м)")
    plt.ylabel("Высота (м)")
    plt.title("Оптимальная траектория полета снаряда")
    plt.legend()
    plt.grid()
    plt.show()
else:
    print("Не удалось найти подходящий угол. Проверьте входные данные.")
