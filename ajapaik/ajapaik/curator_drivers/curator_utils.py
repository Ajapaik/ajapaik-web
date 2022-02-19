from ajapaik.ajapaik.models import AlbumPhoto, Photo, Album


def handle_existing_photos(existing_photo: Photo, transformed_item: dict):
    if existing_photo:
        transformed_item['ajapaikId'] = existing_photo.id
        album_ids = AlbumPhoto.objects.filter(photo=existing_photo).values_list('album_id', flat=True)
        transformed_item['albums'] = list(Album.objects.filter(pk__in=album_ids, atype=Album.CURATED)
                                          .values_list('id', 'name').distinct())

    return transformed_item
