import os
from sorl.thumbnail.base import ThumbnailBackend, EXTENSIONS
from sorl.thumbnail.conf.defaults import THUMBNAIL_PREFIX
from sorl.thumbnail.helpers import tokey, serialize


class SEOThumbnailBackend(ThumbnailBackend):
    def _get_thumbnail_filename(self, source, geometry_string, options):
        key = tokey(source.key, geometry_string, serialize(options))

        filename, _ext = os.path.splitext(os.path.basename(source.name))

        path = '%s/%s' % (key, filename)

        return '%s%s.%s' % (THUMBNAIL_PREFIX, path, EXTENSIONS[options['format']])
