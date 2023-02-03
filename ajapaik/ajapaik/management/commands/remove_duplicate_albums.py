# encoding: utf-8
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Count

from ajapaik.ajapaik.models import Album, AlbumPhoto, Points
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle, FaceRecognitionRectangleFeedback, \
    FaceRecognitionUserSuggestion


class Command(BaseCommand):
    help = "Removes duplicate albums with the same name"

    def handle(self, *args, **options):
        for language in settings.MODELTRANSLATION_LANGUAGES:
            attribute = f'name_{language}'
            duplicates = Album.objects.values(attribute) \
                .annotate(name_count=Count(attribute)) \
                .filter(name_count__gt=1)

            for duplicate in duplicates:
                if duplicate[attribute] is None or duplicate[attribute] == '' or duplicate[attribute].isspace():
                    continue
                filter_dict = {attribute: duplicate[attribute]}
                all_albums = Album.objects.filter(**filter_dict).order_by('created')
                first_instance = all_albums.first()
                existing_links_to_photo = AlbumPhoto.objects.filter(album_id=first_instance.id).values_list('photo_id')
                other_instances = all_albums.exclude(id=first_instance.id)
                other_instance_ids = other_instances.values_list('id')
                new_list = []

                if first_instance.subalbum_of in other_instances:
                    first_instance.subalbum_of = None
                    first_instance.save()
                    first_instance = all_albums.first()

                albums_linking_to_other_instances = Album.objects.filter(
                    subalbum_of_id__in=other_instance_ids
                )

                if albums_linking_to_other_instances is not None:
                    for link in albums_linking_to_other_instances:
                        link.subalbum_of = first_instance
                        link.save(update_fields=["subalbum_of"])
                        link.save()

                for other_instance in other_instances:
                    if other_instance.muis_person_ids is None:
                        continue
                    new_list.extend(other_instance.muis_person_ids)
                if first_instance.muis_person_ids is not None:
                    extended_list = first_instance.muis_person_ids
                else:
                    extended_list = []
                extended_list.extend(new_list)
                new_set = set(extended_list)
                first_instance.muis_person_ids = list(new_set)
                first_instance.light_save()

                AlbumPhoto.objects.filter(
                    album_id__in=other_instance_ids,
                    photo_id__in=existing_links_to_photo
                ).delete()

                album_photos = AlbumPhoto.objects.filter(album_id__in=other_instance_ids)
                if album_photos is not None:
                    for albumphoto in album_photos:
                        albumphoto.album = first_instance
                    AlbumPhoto.objects.bulk_update(album_photos, ['album'])

                rectangles = FaceRecognitionRectangle.objects.filter(
                    subject_ai_suggestion_id__in=other_instance_ids
                )
                if rectangles is not None:
                    for rectangle in rectangles:
                        rectangle.subject_ai_suggestion = first_instance
                    FaceRecognitionRectangle.objects.bulk_update(rectangles, ['subject_ai_suggestion'])

                rectangles = FaceRecognitionRectangle.objects.filter(
                    subject_consensus_id__in=other_instance_ids
                )
                if rectangles is not None:
                    for rectangle in rectangles:
                        rectangle.subject_consensus = first_instance
                    FaceRecognitionRectangle.objects.bulk_update(rectangles, ['subject_consensus'])

                feedbacks = FaceRecognitionRectangleFeedback.objects.filter(
                    alternative_subject_id__in=other_instance_ids
                )
                if feedbacks is not None:
                    for feedback in feedbacks:
                        feedback.alternative_subject = first_instance
                    FaceRecognitionRectangleFeedback.objects.bulk_update(feedbacks, ['alternative_subject'])

                suggestions = FaceRecognitionUserSuggestion.objects.filter(
                    subject_album_id__in=other_instance_ids
                )
                if suggestions is not None:
                    for suggestion in suggestions:
                        suggestion.subject_album = first_instance
                    FaceRecognitionUserSuggestion.objects.bulk_update(suggestions, ['subject_album'])

                points = Points.objects.filter(album_id__in=other_instance_ids)
                if points is not None:
                    for point in points:
                        point.album = first_instance
                    Points.objects.bulk_update(points, ['album'])
                other_instances.delete()
                first_instance.set_calculated_fields()
                first_instance.save()
