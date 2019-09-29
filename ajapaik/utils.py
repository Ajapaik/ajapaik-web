from math import cos, sin, radians, atan2, sqrt


# FIXME: Ugly functions, make better or import from whatever library we have anyway
def calculate_thumbnail_size(p_width, p_height, desired_longest_side):
    if p_width and p_height:
        w = float(p_width)
        h = float(p_height)
        desired_longest_side = float(desired_longest_side)
        if w > h:
            desired_width = desired_longest_side
            factor = w / desired_longest_side
            desired_height = h / factor
        else:
            desired_height = desired_longest_side
            factor = h / desired_longest_side
            desired_width = w / factor
    else:
        return 400, 300

    return int(desired_width), int(desired_height)


def calculate_thumbnail_size_max_height(p_width, p_height, desired_height):
    w = float(p_width)
    h = float(p_height)
    desired_height = float(desired_height)
    factor = h / desired_height
    desired_width = w / factor

    return int(desired_width), int(desired_height)


def convert_to_degrees(value):
    d0 = value[0][0]
    d1 = value[0][1]
    d = float(d0) / float(d1)

    m0 = value[1][0]
    m1 = value[1][1]
    m = float(m0) / float(m1)

    s0 = value[2][0]
    s1 = value[2][1]
    s = float(s0) / float(s1)

    return d + (m / 60.0) + (s / 3600.0)


def angle_diff(angle1, angle2):
    diff = angle2 - angle1
    if diff < -180:
        diff += 360
    elif diff > 180:
        diff -= 360
    return abs(diff)


def average_angle(angles):
    x = y = 0
    for e in angles:
        x += cos(radians(e))
        y += sin(radians(e))
    return atan2(y, x)


def distance_in_meters(lon1, lat1, lon2, lat2):
    lat_coeff = cos(radians((lat1 + lat2) / 2.0))
    return (2 * 6350e3 * 3.1415 / 360) * sqrt((lat1 - lat2) ** 2 + ((lon1 - lon2) * lat_coeff) ** 2)

def most_frequent(List): 
    counter = 0
    num = List[0]
    uniques = list(set(List))
      
    for i in uniques: 
        currentFrequency = List.count(i) 
        if(currentFrequency >= counter): 
            counter = currentFrequency 
            num = i 
    return num

def least_frequent(List): 
    counter = None
    num = List[0]
    uniques = list(set(List))
      
    for i in uniques: 
        currentFrequency = List.count(i) 
        if(counter == None or currentFrequency < counter): 
            counter = currentFrequency 
            num = i
    return num 