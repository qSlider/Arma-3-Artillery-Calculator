import math

def calculate_elevation_with_height(R, v, h_s, h_t, g=9.79):
    max_R = v ** 2 / g
    if R > max_R:
        return "Дальність неможлива"

    arg = (R * g) / (v ** 2)
    theta_rad = math.asin(arg) / 2

    delta_h = h_t - h_s
    theta_correction_rad = math.atan(delta_h / R)

    theta_new_rad = theta_rad + theta_correction_rad
    theta_mil = theta_new_rad * (6400 / (2 * math.pi))
    return round(theta_mil)

def calculate_high_elevation(R, v, h_s, h_t, g=9.79):
    '''
    R - Horizontal distance to the target (m)
    v - Initial velocity of the projectile (m/s)
    h_s - Height of the shooter (m)
    h_t - Target height (m)
    g - Free fall acceleration (m/s²)
    '''
    delta_h = h_t - h_s

    A = (g * R ** 2) / (2 * v ** 2)
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

    theta_high = max(theta1, theta2)
    theta_mil = theta_high * (6400 / (2 * math.pi))

    return round(theta_mil)

def mil_to_rad(mils):
    return mils * (2 * math.pi / 6400)

def calculate_range(v, theta_rad, h_s=0, h_t=0, g=9.79):
    '''
    Возвращает дальность полета с учетом разницы высот
    '''
    if h_s == h_t:
        R = (v ** 2) * math.sin(2 * theta_rad) / g
        return R
    else:
        # Решение через кинематику с разницей высот
        vx = v * math.cos(theta_rad)
        vy = v * math.sin(theta_rad)
        delta_h = h_t - h_s

        discriminant = vy ** 2 + 2 * g * delta_h
        if discriminant < 0:
            return None

        t = (vy + math.sqrt(discriminant)) / g
        R = vx * t
        return R

def range_difference_for_1mil(v, theta_mil, h_s=0, h_t=0, g=9.79):
    theta_rad = mil_to_rad(theta_mil)
    theta_plus_1_rad = mil_to_rad(theta_mil + 1)

    r1 = calculate_range(v, theta_rad, h_s, h_t, g)
    r2 = calculate_range(v, theta_plus_1_rad, h_s, h_t, g)

    if r1 is None or r2 is None:
        return "Недоступно"

    return r2 - r1

def calculate_flight_time(v, theta_rad, h_s=0, h_t=0, g=9.79):
    """
    v - начальная скорость (м/с)
    theta_rad - угол в радианах
    h_s - высота стрелка (м)
    h_t - высота цели (м)
    g - ускорение свободного падения (м/с²)
    Возвращает время полета в секундах
    """
    vx = v * math.cos(theta_rad)
    vy = v * math.sin(theta_rad)
    delta_h = h_t - h_s

    discriminant = 2 * vy + 2 * g * delta_h
    if discriminant < 0:
        return "Цель недостижима (по высоте)"

    t = (vy + math.sqrt(discriminant)) / g
    return t

print(calculate_elevation_with_height(1900, 167.7, 0, 0))
print(calculate_high_elevation(4000, 226.6, 0, 100))
theta_mil = 240
v = 200
print(f"Δдальность на 1 mil при {theta_mil} mil:", range_difference_for_1mil(v, theta_mil, 0, 0))
print (f"Время полета :" , calculate_flight_time(v, theta_mil, 0, 0))