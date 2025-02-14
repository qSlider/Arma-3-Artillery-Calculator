import math
import numpy as np


class ArtilleryCalculator:
    DEG_TO_MILS = 6400 / 360  # Константа для перевода градусов в миллирадианы

    def __init__(self):
        self.DEFAULT_AIR_FRICTION = -0.00006
        self.MK6_82mm_AIR_FRICTION = -0.0001

    def calculate_muzzle_velocity(self, muzzle_velocity, temperature):
        """Корректировка начальной скорости с учетом температуры"""
        return muzzle_velocity * (((temperature + 273.13) / 288.13 - 1) / 40 + 1)

    def simulate_shot(self, angle_mils, target_height, muzzle_velocity,
                      air_friction, cross_wind, tail_wind, temperature, air_density):
        """Симуляция полета снаряда с учетом атмосферных условий"""
        # Конвертация угла в радианы
        angle = math.radians(angle_mils / self.DEG_TO_MILS)

        # Корректировка скорости
        muzzle_velocity = self.calculate_muzzle_velocity(muzzle_velocity, temperature)

        # Параметры симуляции
        dt = 0.1  # Шаг времени (сек)
        g = 9.80665  # Ускорение свободного падения
        density_ratio = air_density / 1.225

        # Начальные условия
        vx = muzzle_velocity * math.cos(angle) + tail_wind
        vy = muzzle_velocity * math.sin(angle)
        x, y, z = 0.0, 0.0, 0.0
        time = 0.0

        while z >= target_height:
            # Обновление скорости с учетом сопротивления воздуха
            speed = math.sqrt(vx ** 2 + vy ** 2)
            drag = air_friction * density_ratio * speed ** 2 * dt

            vx -= drag * vx
            vy -= (g + drag * vy) * dt

            # Обновление позиции
            x += vx * dt
            z += vy * dt - 0.5 * g * dt ** 2
            time += dt

            # Проверка пересечения высоты цели
            if z <= target_height:
                break

        # Расчет бокового смещения от ветра
        x_deviation = cross_wind * time
        return x_deviation, x, time

    def calculate_elevation(self, target_distance, target_height, muzzle_velocity,
                            high_arc=True, air_friction=0, cross_wind=0, tail_wind=0,
                            temperature=15, air_density=1.225, max_iter=20, tolerance=0.5):
        """Итеративный расчет угла возвышения"""
        if air_friction != 0:
            muzzle_velocity = self.calculate_muzzle_velocity(muzzle_velocity, temperature)

        # Начальные предположения для угла
        angle = 800 if high_arc else 200  # В миллирадианах
        use_distance = target_distance
        result_distance = 0
        iterations = 0

        while abs(result_distance - target_distance) > tolerance and iterations < max_iter:
            # Симуляция выстрела
            x_dev, result_distance, tof = self.simulate_shot(
                angle, target_height, muzzle_velocity, air_friction,
                cross_wind, tail_wind, temperature, air_density
            )

            # Корректировка угла
            error = target_distance - result_distance
            angle += error * 0.1  # Простая пропорциональная коррекция
            iterations += 1

        # Расчет поправки по азимуту
        angle_offset = -math.degrees(math.atan2(x_dev, result_distance)) * self.DEG_TO_MILS
        return angle, angle_offset, tof

    def calculate_solution(self, gun_pos, target_pos, muzzle_velocity, high_arc=True,
                           air_friction=0, temperature=15, air_density=1.225,
                           wind_dir=0, wind_speed=0):
        """Основная функция расчета решения"""
        # Расчет относительного положения
        rel_pos = np.array(target_pos) - np.array(gun_pos)
        target_dir = math.degrees(math.atan2(rel_pos[0], rel_pos[1]))
        target_dist = math.hypot(rel_pos[0], rel_pos[1])
        height_diff = rel_pos[2]

        # Разложение ветра на составляющие
        wind_angle = math.radians(wind_dir - target_dir)
        cross_wind = math.sin(wind_angle) * wind_speed
        tail_wind = -math.cos(wind_angle) * wind_speed

        # Расчет углов
        return self.calculate_elevation(
            target_dist, height_diff, muzzle_velocity, high_arc, air_friction,
            cross_wind, tail_wind, temperature, air_density
        )


# Пример использования
if __name__ == "__main__":
    calculator = ArtilleryCalculator()

    # Параметры выстрела
    gun_position = [0, 0, 0]
    target_position = [500, 300, 10]
    muzzle_vel = 200
    air_fric = -6e-05

    # Расчет решения
    solution = calculator.calculate_solution(
        gun_position, target_position, muzzle_vel,
        high_arc=True, air_friction=air_fric,
        wind_dir=45, wind_speed=5
    )

    print(f"Угол возвышения: {solution[0]:.1f} мил")
    print(f"Поправка по азимуту: {solution[1]:.1f} мил")
    print(f"Время полета: {solution[2]:.1f} сек")