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





print(calculate_elevation_with_height(1900, 167.7, 0, 0))
print(calculate_high_elevation(4000, 226.6, 0, 100))
