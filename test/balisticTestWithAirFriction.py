import math

def calculate_elevation_with_air_friction(R, v, h_s, h_t, air_friction=-6e-05, g=9.79):
    # Применяем коэффициент сопротивления воздуха
    v_corrected = v * (1 + air_friction * R)  # Скорость с учетом сопротивления

    max_R = v_corrected ** 2 / g
    if R > max_R:
        return "Дальність неможлива"

    # Рассчитываем угол в радианах для дальности без учета высот
    arg = (R * g) / (v_corrected ** 2)
    theta_rad = math.asin(arg) / 2

    # Коррекция угла для разницы высот
    delta_h = h_t - h_s
    theta_correction_rad = math.atan(delta_h / R)

    # Новый угол с учетом высоты и скорости с учетом сопротивления
    theta_new_rad = theta_rad + theta_correction_rad

    # Переводим в мили (угол в радианах * 6400 / 2π)
    theta_mil = theta_new_rad * (6400 / (2 * math.pi))
    return round(theta_mil)

def calculate_high_elevation_with_air_friction(R, v, h_s, h_t, air_friction=-6e-05, g=9.79):
    '''
    R - Горизонтальная дистанция до цели (м)
    v - Начальная скорость снаряда (м/с)
    h_s - Высота стреляющего (м)
    h_t - Высота цели (м)
    air_friction - Коэффициент сопротивления воздуха
    g - Ускорение свободного падения (м/с²)
    '''
    # Применяем коэффициент сопротивления воздуха
    v_corrected = v * (1 + air_friction * R)  # Скорость с учетом сопротивления

    delta_h = h_t - h_s

    A = (g * R ** 2) / (2 * v_corrected ** 2)
    B = -R
    C = A + delta_h

    discriminant = B ** 2 - 4 * A * C

    if discriminant < 0:
        return "Дальність неможлива"

    sqrt_discriminant = math.sqrt(discriminant)

    T1 = (-B + sqrt_discriminant) / (2 * A)
    T2 = (-B - sqrt_discriminant) / (2 * A)

    theta1 = math.atan(T1)
    theta2 = math.atan(T2)

    # Выбираем максимальный угол
    theta_high = max(theta1, theta2)

    # Переводим угол в мили (угол в радианах * 6400 / 2π)
    theta_mil = theta_high * (6400 / (2 * math.pi))

    return round(theta_mil)


# Пример использования:

# Рассчитываем угол возвышения для дальности 2000 метров с учетом высоты и сопротивления воздуха
print(calculate_elevation_with_air_friction(2000, 179.4, 0, 0))  # Без высот и с сопротивлением
print(calculate_high_elevation_with_air_friction(2600, 179.4, 0, 0))  # С учетом высоты цели и сопротивления
