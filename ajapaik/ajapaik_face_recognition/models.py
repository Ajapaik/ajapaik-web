import json

from django.db import models
from django.utils.translation import ugettext_lazy as _

from ajapaik.ajapaik.models import Photo, Profile, Album


# TODO: Delete this once we can (migrations are okay, etc.)
class FaceRecognitionSubject(models.Model):
    MALE, FEMALE = range(2)
    GENDER_CHOICES = (
        (FEMALE, _('Female')),
        (MALE, _('Male'))
    )
    name = models.CharField(max_length=255)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.PositiveSmallIntegerField(choices=GENDER_CHOICES, blank=True, null=True)
    is_public_figure = models.BooleanField(default=False)
    photos = models.ManyToManyField(Photo, related_name='people')
    face_encoding = models.TextField(blank=True, null=True)
    user = models.ForeignKey(Profile)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s' % self.name


class FaceRecognitionRectangle(models.Model):
    photo = models.ForeignKey(Photo, related_name='face_recognition_rectangles')
    subject_consensus = models.ForeignKey(Album, null=True, blank=True,
                                          related_name='face_recognition_crowdsourced_rectangles')
    subject_ai_guess = models.ForeignKey(Album, null=True, blank=True,
                                         related_name='face_recognition_ai_detected_rectangles')
    # If no user is attached, means OpenCV detected it
    user = models.ForeignKey(Profile, blank=True, null=True, related_name='face_recognition_rectangles')
    # (top, right, bottom, left)
    coordinates = models.TextField()
    # Users can have it deleted, but we'll keep records in our DB in case of malice
    deleted = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s - %s - %s' % (self.id, self.photo, self.user)

    def decode_coordinates(self):
        return json.loads(self.coordinates)


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
    subject_album = models.ForeignKey(Album, related_name='face_recognition_guesses')
    rectangle = models.ForeignKey(FaceRecognitionRectangle, related_name='face_recognition_guesses')
    # Empty user means OpenCV recognized the face automatically
    user = models.ForeignKey(Profile, related_name='face_recognition_guesses', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s - %s - %s - %s' % (self.id, self.rectangle, self.user, self.subject)
