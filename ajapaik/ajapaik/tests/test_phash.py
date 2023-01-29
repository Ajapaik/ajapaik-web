from PIL import Image, ImageDraw

from ajapaik.ajapaik.phash import binary_hash_to_signed_integer, phash


def test_binary_hash_to_signed_integer():
    assert (binary_hash_to_signed_integer([True, False, False, True, False,
                                           False, False, False, True, False,
                                           True, True, True, True, False,
                                           True, True, True, False, True,
                                           True, True, True, False, True,
                                           False, True, False, False, False,
                                           False, False, False, True, True,
                                           True, True, False, False, False,
                                           True, False, False, False, True,
                                           False, True, False, False, True,
                                           False, False, True, True, True,
                                           False, True, True, False, False,
                                           True, False, True, True])) == -8017006980851151157
    assert binary_hash_to_signed_integer([True] * 64) == -1
    assert binary_hash_to_signed_integer([False] * 64) == 0


def test_phash():
    triangles_image = Image.new('RGBA', (64, 64), (152, 75, 32))
    draw = ImageDraw.Draw(triangles_image)
    draw.polygon([(0, 10), (64, 64), (100, 20)], fill=(255, 0, 0))
    draw.polygon([(20, 10), (64, 64), (150, 50)], fill='yellow')

    assert phash(triangles_image) == -5164139871937651366
    assert phash(Image.new('RGBA', (64, 64), (255, 255, 255, 0))) == -9223372036854775808
    assert phash(Image.new('RGBA', (64, 64), (0, 0, 0, 0))) == 0
