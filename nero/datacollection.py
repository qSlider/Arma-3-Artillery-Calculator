import csv
import os
import sys


# Получаем базовую директорию (где .exe или .py)
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FILENAME = os.path.join(BASE_DIR, "fire_log.csv")

# Поля таблицы
FIELDS = [
    "Artillery",
    "Shell",
    "Charge",
    "Distance",
    "Azimuth",
    "Elevation",
    "Hit",
    "Temperature",
    "Pressure",
    "AirFriction",
    "Flight Time"
]


def create_csv_if_not_exists():
    if not os.path.exists(FILENAME):
        with open(FILENAME, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS, delimiter=';')
            writer.writeheader()
        print(f"[INFO] Файл {FILENAME} создан.")

def log_fire_data(temperature, pressure, air_friction, flight_time=""):
    print("\nВведите данные стрельбы:")

    entry = {
        "Artillery": input("Имя артиллерии: "),
        "Shell": input("Название снаряда: "),
        "Charge": input("Заряд (например, 1, 2, 3): "),
        "Distance": input("Дистанция (в метрах): "),
        "Azimuth": input("Азимут (в градусах): "),
        "Elevation": input("Угол возвышения (в градусах): "),
        "Hit": input("Попадание? (True/False): ").capitalize(),
        "Temperature": temperature,
        "Pressure": pressure,
        "AirFriction": air_friction,
        "Flight Time": flight_time if flight_time else input("Время полета (в секундах): ")
    }

    if entry["Hit"] not in ["True", "False"]:
        print("[ОШИБКА] Значение 'Hit' должно быть 'True' или 'False'. Попробуйте снова.")
        return

    with open(FILENAME, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS, delimiter=';')
        writer.writerow(entry)

    print("[✔] Данные успешно записаны.")


if __name__ == "__main__":
    create_csv_if_not_exists()
    while True:
        log_fire_data("", "", "")
        again = input("Добавить еще одну запись? (y/n): ").lower()
        if again != 'y':
            break