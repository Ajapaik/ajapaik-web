import json

from django.db import models
from django.db.models import CASCADE
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.contrib.gis.db.models import DateTimeField, ImageField
from ajapaik.utils import most_frequent

from ajapaik.ajapaik.models import Album, Photo, Points, Profile

YOUNG, MIDDLEAGE, OLD, UNKNOWN, NOT_APPLICABLE = range(5)
AGE = (
    (YOUNG, _("Young")),
    (MIDDLEAGE, _("Middleage")),
    (OLD, _("Old")),
    (UNKNOWN, _("Unknown")),
    (NOT_APPLICABLE, _("Not Applicable"))
)
FEMALE, MALE, UNKNOWN, NOT_APPLICABLE = range(4)
GENDER = (
    (FEMALE, _('Female')),
    (MALE, _('Male')),
    (UNKNOWN, _("Unknown")),
    (NOT_APPLICABLE, _("Not Applicable"))
)

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
    gender = models.PositiveSmallIntegerField(choices=GENDER, blank=True, null=True)
    age = models.PositiveSmallIntegerField(choices=AGE, blank=True, null=True)
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
    
    def add_subject_data(subject, profile, age, gender):
        lastGuesses = FaceRecognitionRectangleSubjectDataGuess.objects.filter(face_recognition_rectangle_id = subject.id).order_by('guesser_id', '-created').all().distinct('guesser_id')
        lastGuessByCurrentUser = lastGuesses.filter(guesser_id=profile.id).first()
        lastGuessesByOtherUsers = lastGuesses.exclude(guesser_id=profile.id)
        guessGender = gender
        if gender == 3:
           guessGender = subject.subject_consensus.gender
        newGuess = FaceRecognitionRectangleSubjectDataGuess(face_recognition_rectangle = subject, guesser = profile, gender = guessGender, age = age)
        newGuess.save()
        if lastGuessesByOtherUsers.count() > 0:
            results = {}
            sumGender = 0
            guessCountGender = 0
            sumAge = 0
            guessCountAge = 0
            if gender != None:
                sumGender = int(gender, 10)
                guessCountGender = 1
            if age != None:
                sumAge = int(age, 10)
                guessCountAge = 1
            unknowns = {
                "age": 0,
                "gender": 0
            }
            ageGuesses = []
            genderGuesses = []
            for guess in lastGuessesByOtherUsers:
                if(guess.age != None and guess.age != 4):
                    ageGuesses.append(guess.age)
                if(guess.gender != None and guess.gender != 3):
                    genderGuesses.append(guess.age)
            if len(ageGuesses) > 0:
                subject.age = most_frequent(ageGuesses)
            else:
                subject.age = 4
            if len(genderGuesses) > 0:
                subject.gender = most_frequent(genderGuesses)
            else:
                subject.gender = 3
        else:
            subject.age = age
            subject.gender = gender
        subject.save()
        points = 0
        if(lastGuessByCurrentUser is None and int(age) < 3):
            ageGuessPoints = 20
            Points(
                action=Points.GUESS_SUBJECT_AGE,
                annotation = subject,
                created=timezone.now(),
                face_recognition_rectangle_subject_data_guess = newGuess,
                points=ageGuessPoints,
                user=profile
            ).save()
            points += ageGuessPoints
        if(lastGuessByCurrentUser is None and int(gender) < 2):
            genderGuessPoints = 20
            Points(
                action=Points.GUESS_SUBJECT_GENDER,
                annotation = subject,
                created=timezone.now(),
                face_recognition_rectangle_subject_data_guess = newGuess,
                points=genderGuessPoints,
                user=profile
            ).save()
            points += genderGuessPoints
        return points

class FaceRecognitionRectangleSubjectDataGuess(models.Model):
    face_recognition_rectangle = models.ForeignKey(FaceRecognitionRectangle, on_delete=CASCADE, related_name="face_recognition_rectangle")
    guesser = models.ForeignKey(Profile, on_delete=CASCADE, related_name="subject_data_guesser")
    gender = models.PositiveSmallIntegerField(choices=GENDER, null=True)
    age = models.PositiveSmallIntegerField(choices=AGE, null=True)
    created = DateTimeField(auto_now_add=True, db_index=True)

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
