import numpy as np
import numba as nb
import matplotlib.pyplot as plt
import time

# Константы вынесены глобально для Numba
G = 9.81
K_BASE = 6e-05
RHO_STANDARD = 1.225


def measure_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        exec_time = time.perf_counter() - start_time
        if func.__name__ != 'simulate_trajectory_numba':
            print(f"⏱️ Время выполнения {func.__name__}: {exec_time:.4f} секунд")
        return result

    return wrapper


@nb.njit(fastmath=True, parallel=True)
def find_optimal_angles(v0_corrected, k, distance, height_diff):
    """Параллельный поиск углов с использованием Numba"""
    result = np.zeros(900, dtype=np.float64)
    hit_result = np.zeros(900, dtype=np.bool_)

    # Параллельный цикл
    for i in nb.prange(900):
        angle = i * 0.1  # от 0 до 90 с шагом 0.1
        trajectory, hit = simulate_trajectory_numba(v0_corrected, angle, k, distance, height_diff)
        result[i] = angle
        hit_result[i] = hit

    valid_indices = np.where(hit_result)[0]
    return result[valid_indices[0]] if len(valid_indices) > 0 else None


@nb.njit(fastmath=True, parallel=True)
def find_high_trajectory_angles(v0_corrected, k, distance, height_diff):
    """Параллельный поиск углов высокой траектории"""
    result = np.zeros(440, dtype=np.float64)
    hit_result = np.zeros(440, dtype=np.bool_)
    deviation_result = np.zeros(440, dtype=np.float64)

    # Параллельный цикл
    for i in nb.prange(440):
        angle = 45 + i * 0.1  # от 45 до 89 с шагом 0.1
        trajectory, hit = simulate_trajectory_numba(v0_corrected, angle, k, distance, height_diff)
        result[i] = angle
        hit_result[i] = hit
        deviation_result[i] = abs(trajectory[-1, 0] - distance) + abs(
            trajectory[-1, 1] - height_diff) if hit else np.inf

    valid_indices = np.where(hit_result)[0]
    return result[valid_indices[np.argmin(deviation_result[valid_indices])]] if len(valid_indices) > 0 else None


@nb.njit(fastmath=True)
def simulate_trajectory_numba(v0, angle, k, target_distance, target_height, dt=0.01):
    """Высокооптимизированная функция траектории с Numba"""
    angle = np.radians(angle)
    vx, vz = v0 * np.cos(angle), v0 * np.sin(angle)
    x, z = 0.0, 0.0
    trajectory = np.zeros((10000, 2))
    idx = 0

    while x <= target_distance and z >= min(0, target_height):
        v = np.sqrt(vx ** 2 + vz ** 2)
        dvx_dt = -k * vx * v
        dvz_dt = -G - k * vz * v
        vx += dvx_dt * dt
        vz += dvz_dt * dt
        x += vx * dt
        z += vz * dt

        trajectory[idx] = [x, z]
        idx += 1

        if abs(x - target_distance) < 10.0 and abs(z - target_height) < 10.0:
            return trajectory[:idx], True

    return trajectory[:idx], False


@measure_execution_time
def find_optimal_angle(v0, distance, height_diff, temperature, pressure, k_base, plot=False):
    """Обертка для оптимального угла с поддержкой визуализации"""
    pressure_pa = pressure * 100
    temperature_k = temperature + 273.15
    R = 287.05
    rho_calculated = pressure_pa / (R * temperature_k)
    rho_ratio = rho_calculated / RHO_STANDARD
    k = k_base * rho_ratio
    v0_corrected = v0 * np.sqrt((temperature + 273.15) / 288.15)

    optimal_angle = find_optimal_angles(v0_corrected, k, distance, height_diff)

    if plot and optimal_angle is not None:
        trajectory, _ = simulate_trajectory_numba(v0_corrected, optimal_angle, k, distance, height_diff)
        plt.figure(figsize=(10, 5))
        plt.plot(trajectory[:, 0], trajectory[:, 1], label=f"Угол: {optimal_angle:.2f}°")
        plt.scatter(distance, height_diff, color='red', label='Цель')
        plt.xlabel("Дистанция (м)")
        plt.ylabel("Высота (м)")
        plt.title("Траектория снаряда")
        plt.legend()
        plt.grid()
        plt.savefig("trajectory_plot.png")
        plt.close()

    return optimal_angle


@measure_execution_time
def find_high_trajectory(v0, distance, height_diff, temperature, pressure, k_base, plot=False):
    """Обертка для высокой траектории с поддержкой визуализации"""
    pressure_pa = pressure * 100
    temperature_k = temperature + 273.15
    R = 287.05
    rho_calculated = pressure_pa / (R * temperature_k)
    rho_ratio = rho_calculated / RHO_STANDARD
    k = k_base * rho_ratio
    v0_corrected = v0 * np.sqrt(temperature_k / 288.15)

    best_angle = find_high_trajectory_angles(v0_corrected, k, distance, height_diff)

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


def main():
    print("🚀 Калькулятор траектории снаряда")
    print("------------------------------")

    # Ввод начальных параметров
    v0 = float(input("Введите начальную скорость (м/с): "))
    distance = float(input("Введите дистанцию до цели (м): "))
    height_diff = float(input("Введите разницу высот (м): "))
    temperature = float(input("Введите температуру воздуха (°C): "))
    pressure = float(input("Введите атмосферное давление (гПа): "))

    # Выбор режима расчета
    print("\nВыберите режим:")
    print("1. Оптимальный угол")
    print("2. Высокая траектория")
    mode = input("Введите номер режима (1/2): ")

    # Базовый коэффициент сопротивления воздуха
    k_base = 6e-05

    try:
        if mode == '1':
            result = find_optimal_angle(v0, distance, height_diff, temperature, pressure, k_base, plot=True)
            print(f"\n🎯 Оптимальный угол: {result:.2f}°")
        elif mode == '2':
            result = find_high_trajectory(v0, distance, height_diff, temperature, pressure, k_base, plot=True)
            print(f"\n📐 Угол высокой траектории: {result:.2f}°")
        else:
            print("❌ Неверный режим!")

    except Exception as e:
        print(f"❗ Ошибка при расчете: {e}")


if __name__ == "__main__":
    main()