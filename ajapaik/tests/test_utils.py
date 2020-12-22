import os
import hashlib
from datetime import datetime
from PIL import Image
from ajapaik.utils import average_angle, angle_diff, convert_to_degrees, get_etag, calculate_thumbnail_size, \
    calculate_thumbnail_size_max_height, distance_in_meters, last_modified, least_frequent, most_frequent


def test_get_etag():
    source = 'test_image.png'
    white = Image.new('RGBA', (32, 32), (255, 255, 255, 0))
    white.save("test_image.png", "PNG")

    m = hashlib.md5()
    with open(source, 'rb') as f:
        m.update(f.read())
    result = m.hexdigest()
    assert get_etag(None, 'test_image.png', None) == result

    os.remove(source)
    assert get_etag(None, 'test_image.png', None) is None


def test_last_modified():
    source = 'test_image.png'
    white = Image.new('RGBA', (32, 32), (255, 255, 255, 0))
    white.save("test_image.png", "PNG")

    assert last_modified(None, source, None) == datetime.fromtimestamp(os.path.getmtime(source))

    os.remove(source)
    assert last_modified(None, source, None) is None


def test_least_frequent():
    assert least_frequent((1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5)) == 1


def test_most_frequent():
    assert most_frequent((1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5)) == 5


def test_calculate_thumbnail_size():
    assert calculate_thumbnail_size(400, 800, 500) == (250, 500)
    assert calculate_thumbnail_size(3000, 800, 3000) == (3000, 800)
    assert calculate_thumbnail_size(None, None, 500) == (400, 300)
    assert calculate_thumbnail_size(None, None, None) == (400, 300)


def test_calculate_thumbnail_size_max_height():
    assert calculate_thumbnail_size_max_height(400, 800, 500) == (250, 500)
    assert calculate_thumbnail_size_max_height(3000, 800, 3000) == (11250, 3000)


def test_convert_to_degrees():
    assert convert_to_degrees([[180, 1], [0, 1], [0, 1]]) == 180.0
    assert convert_to_degrees([[40, 1], [20, 1], [50, 1]]) == 40.34722222222222


def test_angle_diff():
    assert angle_diff(0, 0) == 0
    assert angle_diff(0, 360) == 0
    assert angle_diff(360, 0) == 0
    assert angle_diff(360, 360) == 0
    assert angle_diff(170, 540) == 10
    assert angle_diff(540, 10) == 170
    assert angle_diff(-180, 90) == 90
    assert angle_diff(-360, 10) == 10
    assert (angle_diff(-360.55555555555, 10) - 10.55555555555) < 0.000001


def test_average_angle():
    assert average_angle([50, 90, 20, 10]) == 0.7265724896134059
    assert average_angle([15.2523562, 90.643643, -20.532, 10.5235325318]) == 0.364089736050786


def test_distance_in_meters():
    assert distance_in_meters(58.3749359, 26.7294631, 58.3724787, 26.7317836) == 353.96440996564905
    assert distance_in_meters(48.980555, 153.4701513, -54.6574534, -64.1463372) == 25463443.24517036
    assert distance_in_meters(59.4366888, 24.7530732, 58.37782, 26.7288786) == 243147.66265268778
