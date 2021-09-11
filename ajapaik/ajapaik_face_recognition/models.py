import json

from django.contrib.gis.db.models import DateTimeField, ImageField
from django.db import models
from django.db.models import CASCADE
from django.utils import timezone
from django.utils.translation import gettext as _

from ajapaik.ajapaik.models import Album, Photo, Points, Profile
from ajapaik.utils import most_frequent

CHILD, ADULT, ELDERLY, UNKNOWN, NOT_APPLICABLE = range(5)
AGE = (
    (CHILD, _('Child')),
    (ADULT, _('Adult')),
    (ELDERLY, _('Elderly')),
    (UNKNOWN, _('Unknown')),
    (NOT_APPLICABLE, _('Not Applicable'))
)
FEMALE, MALE, UNKNOWN, NOT_APPLICABLE = range(4)
GENDER = (
    (FEMALE, _('Female')),
    (MALE, _('Male')),
    (UNKNOWN, _('Unknown')),
    (NOT_APPLICABLE, _('Not Applicable'))
)


class FaceRecognitionRectangle(models.Model):
    USER, ALGORITHM, PICASA = range(3)
    ORIGIN_CHOICES = (
        (USER, _('User')),
        (ALGORITHM, _('Algorithm')),
        (PICASA, _('Picasa')),
    )

    photo = models.ForeignKey(Photo, related_name='face_recognition_rectangles', on_delete=CASCADE)
    subjectPhoto = ImageField(_('SubjectPhoto'), upload_to='uploads', blank=True, null=True, max_length=255)
    subject_consensus = models.ForeignKey(Album, null=True, blank=True, on_delete=CASCADE,
                                          related_name='face_recognition_crowdsourced_rectangles')
    subject_ai_suggestion = models.ForeignKey(Album, null=True, blank=True, on_delete=CASCADE,
                                              related_name='face_recognition_ai_detected_rectangles')
    # If no user is attached, means OpenCV detected it
    user = models.ForeignKey(Profile, blank=True, null=True, on_delete=CASCADE,
                             related_name='face_recognition_rectangles')
    origin = models.PositiveSmallIntegerField(choices=ORIGIN_CHOICES, default=ALGORITHM)
    gender = models.PositiveSmallIntegerField(choices=GENDER, blank=True, null=True)
    age = models.PositiveSmallIntegerField(choices=AGE, blank=True, null=True)
    # [top, right, bottom, left]
    coordinates = models.TextField()
    face_encoding = models.TextField(null=True, blank=True)
    # Users can have it deleted, but we'll keep records in our DB in case of malice
    deleted = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{str(self.id)} - {str(self.photo)} - {str(self.user)}'

    def decode_coordinates(self):
        return json.loads(self.coordinates)

    def get_subject_name(self):
        subject_album = self.get_subject()

        return subject_album.name if subject_album else None

    def get_subject(self):
        subject_album = None

        # Prefer what people think
        if self.subject_consensus:
            subject_album: Album = self.subject_consensus
        elif self.subject_ai_suggestion:
            subject_album: Album = self.subject_ai_suggestion

        return subject_album

    def add_subject_data(self, profile, age, gender):
        last_suggestions = FaceRecognitionRectangleSubjectDataSuggestion.objects.filter(
            face_recognition_rectangle=self).order_by('proposer_id', '-created').all().distinct('proposer_id')
        last_suggestion_by_current_user = last_suggestions.filter(proposer_id=profile.id).first()
        last_suggestions_by_other_users = last_suggestions.exclude(proposer_id=profile.id)
        if gender == 'SKIP':
            gender = self.subject_consensus.gender
        if gender == 'FEMALE':
            gender = 0
        if gender == 'MALE':
            gender = 1
        if gender == 'UNSURE':
            gender = 2
        if gender == 'NOT_APPLICABLE':
            gender = 3
        if age == 'CHILD':
            age = 0
        if age == 'ADULT':
            age = 1
        if age == 'ELDERLY':
            age = 2
        if age == 'UNSURE':
            age = 3
        if age == 'NOT_APPLICABLE':
            age = 4
        new_suggestion = FaceRecognitionRectangleSubjectDataSuggestion(face_recognition_rectangle=self,
                                                                       proposer=profile, gender=gender, age=age)
        new_suggestion.save()
        self.photo.latest_annotation = new_suggestion.created
        self.photo.light_save()

        if last_suggestions_by_other_users.count() > 0:
            age_suggestions = []
            gender_suggestions = []
            for suggestion in last_suggestions_by_other_users:
                if suggestion.age and suggestion.age != 4:
                    age_suggestions.append(suggestion.age)
                if suggestion.gender and suggestion.gender != 3:
                    gender_suggestions.append(suggestion.age)
            if len(age_suggestions) > 0:
                self.age = most_frequent(age_suggestions)
            else:
                self.age = age
            if len(gender_suggestions) > 0:
                self.gender = most_frequent(gender_suggestions)
            else:
                self.gender = gender
        else:
            self.age = age
            self.gender = gender
        self.save()
        points = 0
        if (last_suggestion_by_current_user is None and int(age) < 3):
            age_suggestion_points = 20
            Points(
                action=Points.SUGGESTION_SUBJECT_AGE,
                annotation=self,
                created=timezone.now(),
                face_recognition_rectangle_subject_data_suggestion=new_suggestion,
                points=age_suggestion_points,
                user=profile
            ).save()
            points += age_suggestion_points
        if (last_suggestion_by_current_user is None and gender is not None and int(gender) < 2):
            gender_suggestion_points = 20
            Points(
                action=Points.SUGGESTION_SUBJECT_GENDER,
                annotation=self,
                created=timezone.now(),
                face_recognition_rectangle_subject_data_suggestion=new_suggestion,
                points=gender_suggestion_points,
                user=profile
            ).save()
            points += gender_suggestion_points
        return points


class FaceRecognitionRectangleSubjectDataSuggestion(models.Model):
    face_recognition_rectangle = models.ForeignKey(FaceRecognitionRectangle, on_delete=CASCADE,
                                                   related_name='face_recognition_rectangle')
    proposer = models.ForeignKey(Profile, on_delete=CASCADE, related_name='subject_data_proposer')
    gender = models.PositiveSmallIntegerField(choices=GENDER, null=True)
    age = models.PositiveSmallIntegerField(choices=AGE, null=True)
    created = DateTimeField(auto_now_add=True, db_index=True)


class FaceRecognitionRectangleFeedback(models.Model):
    rectangle = models.ForeignKey(FaceRecognitionRectangle, on_delete=CASCADE, related_name='feedback')
    user = models.ForeignKey(Profile, on_delete=CASCADE, related_name='face_recognition_rectangle_feedback')
    alternative_subject = models.ForeignKey(Album, on_delete=CASCADE, null=True)
    # So users could downvote bad rectangles
    is_correct = models.BooleanField(default=False)
    is_correct_person = models.BooleanField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        string_label = ''

        if self.is_correct:
            string_label += f'Confirmed annotation {self.rectangle.id}'
        else:
            string_label += f'Rejected annotation {self.rectangle.id}'

        if self.alternative_subject is not None:
            string_label += f', alternative subject suggested: {self.alternative_subject.name}'

        return string_label


class FaceRecognitionUserSuggestion(models.Model):
    USER, ALGORITHM, PICASA = range(3)
    ORIGIN_CHOICES = (
        (USER, _('User')),
        (ALGORITHM, _('Algorithm')),
        (PICASA, _('Picasa')),
    )

    subject_album = models.ForeignKey(Album, on_delete=CASCADE, related_name='face_recognition_suggestions')
    rectangle = models.ForeignKey(FaceRecognitionRectangle, on_delete=CASCADE,
                                  related_name='face_recognition_suggestions')
    # Empty user means OpenCV recognized the face automatically
    user = models.ForeignKey(Profile, on_delete=CASCADE, related_name='face_recognition_suggestions', blank=True,
                             null=True)
    origin = models.PositiveSmallIntegerField(choices=ORIGIN_CHOICES, default=ALGORITHM)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{str(self.id)} - {str(self.rectangle.id)} - {str(self.user.id)} - {str(self.subject_album.id)}'
