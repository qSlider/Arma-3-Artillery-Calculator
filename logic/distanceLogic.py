import math

def calculate_distance(x1, y1, x2, y2):
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance

def calculate_azimuth(x1, y1, x2, y2):
    delta_x = x2 - x1
    delta_y = y2 - y1
    azimuth = math.degrees(math.atan2(delta_y, delta_x))
    azimuth = (azimuth + 360) % 360
    azimuth_in_thousandths = int(azimuth * (6400 / 360))
    return azimuth_in_thousandths

# Example of use:
x1, y1 = 5000, 8000
x2, y2 = 1700, 3000

distance = calculate_distance(x1, y1, x2, y2)
azimuth_in_thousandths = calculate_azimuth(x1, y1, x2, y2)

print("Distance:", distance)
print("Azimuth in thousandths:", azimuth_in_thousandths)
