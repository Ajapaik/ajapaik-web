import json

from django.db import models
from django.utils.translation import ugettext_lazy as _

from project.ajapaik.models import Photo, Profile


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

    class Meta:
        # TODO: Better table naming? Separate schemas for separate apps? Could help isolate testing from PostGIS
        db_table = 'project_face_recognition_subject'

    def __unicode__(self):
        return u'%s' % self.name


class FaceRecognitionRectangle(models.Model):
    photo = models.ForeignKey(Photo, related_name='face_recognition_rectangles')
    subject_consensus = models.ForeignKey(FaceRecognitionSubject, null=True, blank=True,
                                          related_name='crowdsourced_rectangles')
    subject_ai_guess = models.ForeignKey(FaceRecognitionSubject, null=True, blank=True,
                                         related_name='ai_detected_rectangles')
    # If no user is attached, means OpenCV detected it
    user = models.ForeignKey(Profile, blank=True, null=True, related_name='face_recognition_rectangles')
    # (top, right, bottom, left)
    coordinates = models.TextField()
    # Users can have it deleted, but we'll keep records in our DB in case of malice
    deleted = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_face_recognition_rectangle'

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

    class Meta:
        db_table = 'project_face_recognition_rectangle_feedback'

    def __unicode__(self):
        return u'%s - %s - %s - %s' % (self.id, self.rectangle, self.user, self.is_correct)


class FaceRecognitionUserGuess(models.Model):
    subject = models.ForeignKey(FaceRecognitionSubject, related_name='guesses')
    rectangle = models.ForeignKey(FaceRecognitionRectangle, related_name='guesses')
    # Empty user means OpenCV recognized the face automatically
    user = models.ForeignKey(Profile, related_name='face_recognition_guesses', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_face_recognition_user_guess'

    def __unicode__(self):
        return u'%s - %s - %s - %s' % (self.id, self.rectangle, self.user, self.subject)
