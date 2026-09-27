import os

from sorl.thumbnail.base import EXTENSIONS, ThumbnailBackend
from sorl.thumbnail.conf.defaults import THUMBNAIL_PREFIX
from sorl.thumbnail.helpers import serialize, tokey


class SEOThumbnailBackend(ThumbnailBackend):
    def _get_thumbnail_filename(self, source, geometry_string, options):
        key = tokey(source.key, geometry_string, serialize(options))

        filename, _ext = os.path.splitext(os.path.basename(source.name))

        path = f"{key}/{filename}"

        return f"{THUMBNAIL_PREFIX}{path}.{EXTENSIONS[options['format']]}"
