import numpy as np
import numba as nb
import matplotlib.pyplot as plt
import time

g = 9.81
k_base = 6e-05
rho_standard = 1.225

def degrees_to_mil(degrees):
    return degrees * (6400 / 360)

def measure_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        exec_time = time.perf_counter() - start_time
        if func.__name__ != 'simulate_trajectory_numba':
            print(f"⏱️ Время выполнения {func.__name__}: {exec_time:.4f} секунд")
        return result
    return wrapper


def mil_to_degrees(mils):
    return mils * (360 / 6400)


@measure_execution_time
def range_difference_for_1mil_airfriction(v0, angle_mil, temperature=15, pressure=1013, k_base=6e-05, height_diff=0):
    """
    Вычисляет разницу в дальности при изменении угла на 1 mil с учетом сопротивления воздуха

    Параметры:
    v0 (float): начальная скорость снаряда (м/с)
    angle_mil (float): угол в милах
    temperature (float): температура воздуха (°C)
    pressure (float): атмосферное давление (гПа)
    k_base (float): базовый коэффициент сопротивления воздуха
    height_diff (float): разница высот между стрелком и целью (м)

    Возвращает:
    float: разница в дальности при изменении угла на 1 mil (м)
    """
    # Корректировка на основе атмосферных условий (как в ваших существующих функциях)
    pressure_pa = pressure * 100
    temperature_k = temperature + 273.15
    R = 287.05
    rho_calculated = pressure_pa / (R * temperature_k)
    rho_ratio = rho_calculated / rho_standard
    k = k_base * rho_ratio
    v0_corrected = v0 * np.sqrt(temperature_k / 288.15)

    # Конвертируем милы в градусы
    angle_deg = mil_to_degrees(angle_mil)
    angle_plus_1mil_deg = mil_to_degrees(angle_mil + 1)

    # Находим дальность для обоих углов, используя вашу существующую функцию симуляции
    range1 = find_max_range(v0_corrected, angle_deg, k, height_diff)
    range2 = find_max_range(v0_corrected, angle_plus_1mil_deg, k, height_diff)

    if range1 is None or range2 is None:
        return "Недоступно"

    return range2 - range1


def find_max_range(v0, angle, k, height_diff, dt=0.01):
    """
    Вспомогательная функция для определения максимальной дальности полета
    с заданными параметрами
    """
    angle_rad = np.radians(angle)
    vx, vz = v0 * np.cos(angle_rad), v0 * np.sin(angle_rad)
    x, z = 0.0, 0.0

    while z >= min(0, height_diff):
        v = np.sqrt(vx ** 2 + vz ** 2)
        dvx_dt = -k * vx * v
        dvz_dt = -g - k * vz * v
        vx += dvx_dt * dt
        vz += dvz_dt * dt
        x += vx * dt
        z += vz * dt

        # Если достигли высоты цели при нисходящей траектории
        if z <= height_diff and vz < 0:
            # Линейная интерполяция для точного определения дальности
            if z != height_diff:
                prev_z = z - vz * dt
                prev_x = x - vx * dt
                if prev_z != z:  # Избегаем деления на ноль
                    fraction = (height_diff - z) / (prev_z - z)
                    x = x + fraction * (prev_x - x)
            return x

    # Если траектория не пересекает высоту цели
    return None

@nb.njit(fastmath=True)
def simulate_trajectory_numba(v0, angle, k, target_distance, target_height, dt=0.01):
    angle = np.radians(angle)
    vx, vz = v0 * np.cos(angle), v0 * np.sin(angle)
    x, z = 0.0, 0.0
    trajectory = np.zeros((10000, 2))
    idx = 0

    while x <= target_distance and z >= min(0, target_height):
        v = np.sqrt(vx ** 2 + vz ** 2)
        dvx_dt = -k * vx * v
        dvz_dt = -g - k * vz * v
        vx += dvx_dt * dt
        vz += dvz_dt * dt
        x += vx * dt
        z += vz * dt

        trajectory[idx] = [x, z]
        idx += 1

        if abs(x - target_distance) < 10.0 and abs(z - target_height) < 10.0:
            return trajectory[:idx], True

    return trajectory[:idx], False

def simulate_trajectory(v0, angle, k, target_distance, target_height, dt=0.01):
    angle = np.radians(angle)
    vx, vz = v0 * np.cos(angle), v0 * np.sin(angle)
    x, z = 0, 0
    trajectory = []

    while x <= target_distance and z >= min(0, target_height):
        v = np.sqrt(vx ** 2 + vz ** 2)
        dvx_dt = -k * vx * v
        dvz_dt = -g - k * vz * v
        vx += dvx_dt * dt
        vz += dvz_dt * dt
        x += vx * dt
        z += vz * dt
        trajectory.append((x, z))

        if abs(x - target_distance) < 10.0 and abs(z - target_height) < 10.0:
            return np.array(trajectory), True

    return np.array(trajectory), False

@measure_execution_time
def find_optimal_angle(v0, distance, height_diff, temperature, pressure, k_base, plot=False):
    pressure_pa = pressure * 100
    temperature_k = temperature + 273.15
    R = 287.05
    rho_calculated = pressure_pa / (R * temperature_k)
    rho_ratio = rho_calculated / rho_standard
    k = k_base * rho_ratio
    v0_corrected = v0 * np.sqrt((temperature + 273.15) / 288.15)

    optimal_angle = None
    for angle in np.arange(0, 90, 0.1):
        trajectory, hit = simulate_trajectory(v0_corrected, angle, k, distance, height_diff)
        if hit:
            optimal_angle = angle
            if plot:
                plt.figure(figsize=(10, 5))
                plt.plot(trajectory[:, 0], trajectory[:, 1], label=f"Angle: {angle:.2f}°")
                plt.scatter(distance, height_diff, color='red', label='Target')
                plt.xlabel("Distance (m)")
                plt.ylabel("Height (m)")
                plt.title("The trajectory of the shell")
                plt.legend()
                plt.grid()
                plt.savefig("trajectory_plot.png")
                plt.close()
            break

    return optimal_angle

@measure_execution_time
def find_high_trajectory(v0, distance, height_diff, temperature, pressure, k_base, plot=False):
    pressure_pa = pressure * 100
    temperature_k = temperature + 273.15
    R = 287.05
    rho_calculated = pressure_pa / (R * temperature_k)
    rho_ratio = rho_calculated / rho_standard
    k = k_base * rho_ratio
    v0_corrected = v0 * np.sqrt(temperature_k / 288.15)

    best_angle = None
    min_deviation = float('inf')

    for angle in np.arange(45, 89, 0.1):
        trajectory, hit = simulate_trajectory_numba(v0_corrected, angle, k, distance, height_diff)
        if hit:
            deviation = abs(trajectory[-1, 0] - distance) + abs(trajectory[-1, 1] - height_diff)
            if deviation < min_deviation:
                min_deviation = deviation
                best_angle = angle

    if plot and best_angle is not None:
        trajectory, _ = simulate_trajectory_numba(v0_corrected, best_angle, k, distance, height_diff)
        plt.figure(figsize=(10, 5))
        plt.plot(trajectory[:, 0], trajectory[:, 1], label=f"Высокая траектория: {best_angle:.2f}°")
        plt.scatter(distance, height_diff, color='red', label='Цель')
        plt.xlabel("Дистанция (м)")
        plt.ylabel("Высота (м)")
        plt.title("Высокая траектория снаряда")
        plt.legend()
        plt.grid()
        plt.close()

    return best_angle

@measure_execution_time
def calculate_flight_time(v0, angle_deg, k, height_diff, dt=0.01):
    angle_rad = np.radians(angle_deg)
    vx = v0 * np.cos(angle_rad)
    vz = v0 * np.sin(angle_rad)
    x, z = 0.0, 0.0
    t = 0.0

    while z >= min(0, height_diff):
        v = np.sqrt(vx ** 2 + vz ** 2)
        dvx_dt = -k * vx * v
        dvz_dt = -g - k * vz * v
        vx += dvx_dt * dt
        vz += dvz_dt * dt
        x += vx * dt
        z += vz * dt
        t += dt

        if z <= height_diff and vz < 0:
            if z != height_diff:
                prev_z = z - vz * dt
                prev_t = t - dt
                if prev_z != z:
                    fraction = (height_diff - z) / (prev_z - z)
                    t = t + fraction * (-dt)
            return t

    return t


