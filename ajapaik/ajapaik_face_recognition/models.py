import json

from django.db import models
from django.db.models import CASCADE
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.contrib.gis.db.models import DateTimeField, ImageField
from ajapaik.utils import most_frequent

from ajapaik.ajapaik.models import Album, Photo, Points, Profile

CHILD, ADULT, ELDERLY, UNKNOWN, NOT_APPLICABLE = range(5)
AGE = (
    (CHILD, "Child"),
    (ADULT, "Adult"),
    (ELDERLY, "Elderly"),
    (UNKNOWN, "Unknown"),
    (NOT_APPLICABLE, "Not Applicable")
)
FEMALE, MALE, UNKNOWN, NOT_APPLICABLE = range(4)
GENDER = (
    (FEMALE, 'Female'),
    (MALE, 'Male'),
    (UNKNOWN, "Unknown"),
    (NOT_APPLICABLE, "Not Applicable")
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
    subject_ai_guess = models.ForeignKey(Album, null=True, blank=True, on_delete=CASCADE,
                                         related_name='face_recognition_ai_detected_rectangles')
    # If no user is attached, means OpenCV detected it
    user = models.ForeignKey(Profile, blank=True, null=True, on_delete=CASCADE, related_name='face_recognition_rectangles')
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
        subject_album = self.get_subject()

        return subject_album.name if subject_album else None

    def get_subject(self):
        subject_album = None

        # Prefer what people think
        if self.subject_consensus:
            subject_album: Album = self.subject_consensus
        elif self.subject_ai_guess:
            subject_album: Album = self.subject_ai_guess

        return subject_album

    def add_subject_data(subject, profile, age, gender):
        lastGuesses = FaceRecognitionRectangleSubjectDataGuess.objects.filter(face_recognition_rectangle_id = subject.id).order_by('guesser_id', '-created').all().distinct('guesser_id')
        lastGuessByCurrentUser = lastGuesses.filter(guesser_id=profile.id).first()
        lastGuessesByOtherUsers = lastGuesses.exclude(guesser_id=profile.id)
        if gender == "SKIP":
            gender = subject.subject_consensus.gender
        if gender == "FEMALE":
            gender = 0
        if gender == "MALE":
            gender = 1
        if gender == "UNSURE" or gender == "UNKNOWN" or gender == "":
            gender = 2
        if gender == "NOT_APPLICABLE":
            gender = 3
        if age == "CHILD":
            age = 0
        if age == "ADULT":
            age = 1
        if age == "ELDERLY":
            age = 2
        if age == "UNSURE" or age == "UNKNOWN" or age == "":
            age = 3
        if age == "NOT_APPLICABLE":
            age = 4
        newGuess = FaceRecognitionRectangleSubjectDataGuess(face_recognition_rectangle = subject, guesser = profile, gender = gender, age = age)
        newGuess.save()
        if lastGuessesByOtherUsers.count() > 0:
            results = {}
            sumGender = 0
            guessCountGender = 0
            sumAge = 0
            guessCountAge = 0
            if gender != None:
                sumGender = int(str(gender), 10)
                guessCountGender = 1
            if age != None:
                sumAge = int(str(age), 10)
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
                subject.age = age
            if len(genderGuesses) > 0:
                subject.gender = most_frequent(genderGuesses)
            else:
                subject.gender = gender
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
        if(lastGuessByCurrentUser is None and gender is not None and int(gender) < 2):
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
    rectangle = models.ForeignKey(FaceRecognitionRectangle, on_delete=CASCADE, related_name='feedback')
    user = models.ForeignKey(Profile, on_delete=CASCADE, related_name='face_recognition_rectangle_feedback')
    alternative_subject = models.ForeignKey(Album, on_delete=CASCADE, null=True)
    # So users could downvote bad rectangles
    is_correct = models.BooleanField(default=False)
    is_correct_person = models.NullBooleanField()
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

    def __unicode__(self):
        return u'%s - %s - %s - %s' % (self.id, self.rectangle, self.user, self.is_correct)


class FaceRecognitionUserGuess(models.Model):
    USER, ALGORITHM, PICASA = range(3)
    ORIGIN_CHOICES = (
        (USER, _('User')),
        (ALGORITHM, _('Algorithm')),
        (PICASA, _('Picasa')),
    )

    subject_album = models.ForeignKey(Album, on_delete=CASCADE, related_name='face_recognition_guesses')
    rectangle = models.ForeignKey(FaceRecognitionRectangle, on_delete=CASCADE, related_name='face_recognition_guesses')
    # Empty user means OpenCV recognized the face automatically
    user = models.ForeignKey(Profile, on_delete=CASCADE, related_name='face_recognition_guesses', blank=True, null=True)
    origin = models.PositiveSmallIntegerField(choices=ORIGIN_CHOICES, default=ALGORITHM)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s - %s - %s - %s' % (self.id, self.rectangle, self.user, self.subject_album_id)
