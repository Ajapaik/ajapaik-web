import json

from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.gis.db.models import ImageField

from ajapaik.ajapaik.models import Photo, Profile, Album


class FaceRecognitionRectangle(models.Model):
    USER, ALGORITHM, PICASA = range(3)
    ORIGIN_CHOICES = (
        (USER, _('User')),
        (ALGORITHM, _('Algorithm')),
        (PICASA, _('Picasa')),
    )

    photo = models.ForeignKey(Photo, related_name='face_recognition_rectangles')
    subjectPhoto = ImageField(_('SubjectPhoto'), upload_to='uploads', blank=True, null=True, max_length=255)
    subject_consensus = models.ForeignKey(Album, null=True, blank=True,
                                          related_name='face_recognition_crowdsourced_rectangles')
    subject_ai_guess = models.ForeignKey(Album, null=True, blank=True,
                                         related_name='face_recognition_ai_detected_rectangles')
    # If no user is attached, means OpenCV detected it
    user = models.ForeignKey(Profile, blank=True, null=True, related_name='face_recognition_rectangles')
    origin = models.PositiveSmallIntegerField(choices=ORIGIN_CHOICES, default=ALGORITHM)
    # [top, right, bottom, left]
    coordinates = models.TextField()
    face_encoding = models.TextField(null=True, blank=True)
    # Users can have it deleted, but we'll keep records in our DB in case of malice
    deleted = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s - %s - %s' % (self.id, self.photo, self.user)

    def decode_coordinates(self):
        return json.loads(self.coordinates)

    def get_subject_name(self):
        # Prefer what people think
        subject_album = None
        if self.subject_consensus:
            subject_album: Album = self.subject_consensus
        elif self.subject_ai_guess:
            subject_album: Album = self.subject_ai_guess

        return subject_album.name if subject_album else None


class FaceRecognitionRectangleFeedback(models.Model):
    rectangle = models.ForeignKey(FaceRecognitionRectangle, related_name='feedback')
    user = models.ForeignKey(Profile, related_name='face_recognition_rectangle_feedback')
    # So users could downvote bad rectangles
    is_correct = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s - %s - %s - %s' % (self.id, self.rectangle, self.user, self.is_correct)


class FaceRecognitionUserGuess(models.Model):
    USER, ALGORITHM, PICASA = range(3)
    ORIGIN_CHOICES = (
        (USER, _('User')),
        (ALGORITHM, _('Algorithm')),
        (PICASA, _('Picasa')),
    )

    subject_album = models.ForeignKey(Album, related_name='face_recognition_guesses')
    rectangle = models.ForeignKey(FaceRecognitionRectangle, related_name='face_recognition_guesses')
    # Empty user means OpenCV recognized the face automatically
    user = models.ForeignKey(Profile, related_name='face_recognition_guesses', blank=True, null=True)
    origin = models.PositiveSmallIntegerField(choices=ORIGIN_CHOICES, default=ALGORITHM)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s - %s - %s - %s' % (self.id, self.rectangle, self.user, self.subject_album_id)
