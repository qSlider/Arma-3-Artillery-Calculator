import matplotlib
matplotlib.use('TkAgg')  # Використовуємо стандартний backend
import matplotlib.pyplot as plt
import numpy as np

g = 9.81  # Прискорення вільного падіння, м/с²
k_base = 6e-05  # Базовий коефіцієнт опору повітря
rho_standard = 1.225  # Стандартна густина повітря на рівні моря, кг/м³

def degrees_to_mil(degrees):
    return degrees * (6400 / 360)

def simulate_trajectory(v0, angle, k, target_distance, target_height, dt=0.01):
    """ Симуляція траєкторії снаряда """
    angle = np.radians(angle)
    vx, vz = v0 * np.cos(angle), v0 * np.sin(angle)
    x, z = 0, 0
    trajectory = []

    while z >= target_height:
        v = np.sqrt(vx ** 2 + vz ** 2)
        dvx_dt = -k * vx * v
        dvz_dt = -g - k * vz * v

        vx += dvx_dt * dt
        vz += dvz_dt * dt
        x += vx * dt
        z += vz * dt

        trajectory.append((x, z))

        # Перевіряємо потрапляння в ціль з допуском 20 метрів
        if target_height < 0 and x >= target_distance and z <= target_height:
            return np.array(trajectory), True
        elif abs(x - target_distance) < 5.0 and abs(z - target_height) < 5.0:
            return np.array(trajectory), True

    return np.array(trajectory), False

def find_optimal_angle(v0, target_distance, target_height, k, angle_step=0.1):
    """ Пошук оптимального кута для попадання в ціль """
    for angle in np.arange(-10, 90, angle_step):  # Діапазон від -10 до 90 градусів
        trajectory, hit = simulate_trajectory(v0, angle, k, target_distance, target_height)
        if hit:
            return angle  # Знайдено кут попадання

    return None  # Якщо не вдалося знайти кут

# Введення даних
v0 = float(input("Введіть початкову швидкість снаряда (м/с): "))
target_distance = float(input("Введіть відстань до цілі (м): "))
target_height = float(input("Введіть різницю висот (м, позитивне — вище, негативне — нижче): "))
temperature = float(input("Введіть температуру повітря (°C): "))
pressure = float(input("Введіть атмосферний тиск (гПа): "))

# Перерахунок тиску та температури
pressure_pa = pressure * 100  # Па
temperature_k = temperature + 273.15  # Кельвіни
R = 287.05  # Газова стала для сухого повітря
rho_calculated = pressure_pa / (R * temperature_k)  # Густина повітря

print(f"Розрахована густина повітря: {rho_calculated:.2f} кг/м³")

# Коригуємо коефіцієнт опору
rho_ratio = rho_calculated / rho_standard
k = k_base * rho_ratio

# Коригуємо швидкість через температуру
v0 *= np.sqrt((temperature + 273.15) / 288.15)

optimal_angle = find_optimal_angle(v0, target_distance, target_height, k)

if optimal_angle is not None:
    optimal_angle_mil = degrees_to_mil(optimal_angle)
    print(f"Оптимальний кут підйому: {optimal_angle:.2f} градусів ({optimal_angle_mil:.2f} mil)")
    trajectory, _ = simulate_trajectory(v0, optimal_angle, k, target_distance, target_height)

    plt.figure(figsize=(10, 5))
    plt.plot(trajectory[:, 0], trajectory[:, 1], label=f"Траєкторія (кут {optimal_angle:.2f}°)")
    plt.axvline(target_distance, color='r', linestyle='--', label='Ціль')
    plt.axhline(target_height, color='g', linestyle='--', label='Висота цілі')
    plt.xlabel("Відстань (м)")
    plt.ylabel("Висота (м)")
    plt.title("Оптимальна траєкторія польоту снаряда")
    plt.legend()
    plt.grid()
    plt.show()
else:
    print("Не вдалося знайти відповідний кут. Перевірте вхідні дані.")
