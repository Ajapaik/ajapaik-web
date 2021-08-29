from __future__ import (absolute_import, division, print_function)
from typing import List

import numpy
from PIL import Image


class ImageHash(object):
    """
    Hash encapsulation. Can be used for dictionary keys and comparisons.
    """

    def __init__(self, binary_array):
        self.hash = binary_array


def binaryhash_to_signed_integer(hash: List[bool]) -> int:
    result = ""
    for i in hash:
        if i:
            result += '1'
        else:
            result += '0'
    if (result[0] == '1'):
        temp = result[1:].replace('1', '2').replace('0', '1').replace('2', '0')
        return (-1 * int(temp, base=2) - 1)
    return int(result, base=2)


def phash(image:Image, hash_size:int=8, highfreq_factor:int=4) -> int:
    if hash_size < 2:
        raise ValueError('Hash size must be greater than or equal to 2')
    import scipy.fftpack
    img_size = hash_size * highfreq_factor
    image = image.convert('L').resize((img_size, img_size), Image.ANTIALIAS)
    pixels = numpy.asarray(image)
    dct = scipy.fftpack.dct(scipy.fftpack.dct(pixels, axis=0), axis=1)
    dctlowfreq = dct[:hash_size, :hash_size]
    med = numpy.median(dctlowfreq)
    diff = dctlowfreq > med
    result = ImageHash(diff)

    return binaryhash_to_signed_integer(result.hash.flatten())
