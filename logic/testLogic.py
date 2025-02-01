import math


def calculate_high_elevation(R, v, h_s, h_t, g=9.79):
    """
    R  - Горизонтальна відстань до цілі (м)
    v  - Початкова швидкість снаряда (м/с)
    h_s - Висота стрільця (м)
    h_t - Висота цілі (м)
    g  - Прискорення вільного падіння (м/с²)
    """
    delta_h = h_t - h_s

    # Розрахунок коефіцієнтів для квадратного рівняння балістики
    A = (g * R ** 2) / (2 * v ** 2)
    B = -R
    C = A + delta_h

    discriminant = B ** 2 - 4 * A * C

    if discriminant < 0:
        return "Дальність неможлива"

    sqrt_discriminant = math.sqrt(discriminant)

    # Розрахунок двох можливих кутів
    T1 = (-B + sqrt_discriminant) / (2 * A)
    T2 = (-B - sqrt_discriminant) / (2 * A)

    theta1 = math.atan(T1)
    theta2 = math.atan(T2)

    # Вибір більшого кута (висока траєкторія)
    theta_high = max(theta1, theta2)

    # Переведення радіан у мілі
    theta_mil = theta_high * (6400 / (2 * math.pi))

    return round(theta_mil)


print(calculate_high_elevation(14000, 415.3, 0, 100))  # Приклад виклику