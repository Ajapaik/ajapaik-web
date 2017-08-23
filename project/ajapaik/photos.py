import numpy as np

from django.shortcuts import get_object_or_404
from django.conf import settings
from scipy.ndimage import zoom
from scipy import misc
from PIL import Image

from .models import Photo

class PhotoManipulation(object):
    """ Class that provides manipulation for images """

    def image_zoom(self, img, zoom_factor):
        original_image = Image.open(img)

        image_array = misc.fromimage(original_image)

        original_image_height = image_array.shape[0]
        original_image_width = image_array.shape[1]

        #Get height and weight of image from image_array and apply zoom
        image_array_height = int(np.round(zoom_factor * original_image_height))
        image_array_width = int(np.round(zoom_factor * original_image_width))
        zoom_image_value = (zoom_factor,) * 2 + (1,) * (image_array.ndim - 2)

        #Zoom out
        if zoom_factor < 1:
            top = (original_image_height - image_array_height) // 2
            left = (original_image_width - image_array_width) // 2
            zoomed_image = np.zeros_like(original_image)
            zoomed_image[top:top+image_array_height,
                left:left+image_array_width] = zoom(original_image, zoom_image_value)

        #Zoom in
        elif zoom_factor > 1:
            top = (image_array_height - original_image_height) // 2
            left = (image_array_width - original_image_width) // 2

            zoomed_image = zoom(image_array[top:top+image_array_height,
                left:left+image_array_width], zoom_image_value)

            trim_top = ((zoomed_image.shape[0] - original_image_height) // 2)
            trim_left = ((zoomed_image.shape[1] - original_image_width) // 2)

            zoomed_image = zoomed_image[trim_top:trim_top+original_image_height,
                trim_left:trim_left+original_image_width]

        #If zoom_factor is 1
        else:
            zoomed_image = image_array
        # Return scaled image as PIL image
        return {
            'scaled_image': Image.fromarray(zoomed_image)
        }
