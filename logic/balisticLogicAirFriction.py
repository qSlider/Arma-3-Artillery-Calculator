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
                plt.plot(trajectory[:, 0], trajectory[:, 1], label=f"Угол: {angle:.2f}°")
                plt.scatter(distance, height_diff, color='red', label='Цель')
                plt.xlabel("Дистанция (м)")
                plt.ylabel("Высота (м)")
                plt.title("Траектория снаряда")
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

