import logging
import os
import shutil

from django.core.management import BaseCommand
from django.db import connections

from ajapaik import settings

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Clean up thumbnail_kvstore and disk"
    database_name = "default"
    ssd_cache_location = "/media/i910_1/ajapaik/cache"
    ssd_cache_location_for_deletion = "/media/i910_1/ajapaik/cache-delete"
    symlink_location = f"{settings.MEDIA_ROOT}/cache"
    table_name = "thumbnail_kvstore"

    def _my_custom_sql(self):
        with connections[self.database_name].cursor() as cursor:
            cursor.execute(f"DELETE FROM {self.table_name};")

    def _delete_thumbnails(self):
        if os.path.exists(self.ssd_cache_location):
            logger.info('Move folder to temporary location')
            if os.path.exists(self.ssd_cache_location_for_deletion):
                shutil.rmtree(self.ssd_cache_location_for_deletion)
            shutil.move(self.ssd_cache_location, self.ssd_cache_location_for_deletion)
        if os.path.islink(self.symlink_location):
            logger.info('Remove symlink')
            os.remove(self.symlink_location)
        logger.info('Create replacement folder')
        os.makedirs(self.ssd_cache_location)
        logger.info('Create symlink')
        os.symlink(self.ssd_cache_location, self.symlink_location)
        logger.info("You can restart ajapaik application now")
        logger.info("---------------------------------------")
        logger.info('Remove original folder and contents')
        if os.path.exists(self.ssd_cache_location_for_deletion):
            shutil.rmtree(self.ssd_cache_location_for_deletion)

    def handle(self, *args, **options):
        logger.info("Running sql")
        self._my_custom_sql()
        logger.info("Deleting thumbnails")
        self._delete_thumbnails()
