import numpy as np


def calculate_angle_from_distance(own_pos, target_pos, muzzle_velocity, target_dist, high_angle=True,
                                  air_friction=-6e-05, gravity=9.81):
    # Расчет относительного положения цели и орудия
    rel_pos = np.array(target_pos) - np.array(own_pos)
    height_diff = rel_pos[2]

    # Определяем максимальную дальность при максимальном угле (45 градусов)
    max_dist = (muzzle_velocity ** 2) / gravity  # Дальность для угла 45 градусов

    # Если дальность слишком большая или маленькая для простого расчета
    if target_dist > max_dist:
        print("Target is too far for a simple calculation. Air resistance and other factors needed.")
        return None

    # Рассчитываем угол для данной дальности
    angle_rad = 0.5 * np.arcsin((target_dist * gravity) / (muzzle_velocity ** 2))
    angle_deg = np.degrees(angle_rad)

    if high_angle:
        # Используем большую высоту, если необходимо
        return angle_deg + 45  # Ожидаем высокое положение орудия, если это применимо
    return angle_deg


# Пример вызова функции
own_pos = [0, 0, 0]
target_pos = [2000, 0, 0]
muzzle_velocity = 153.9  # скорость снаряда, м/с
target_dist = 2000  # Дистанция до цели в метрах

angle = calculate_angle_from_distance(own_pos, target_pos, muzzle_velocity, target_dist)
print(f"Calculated Angle: {angle} degrees")
