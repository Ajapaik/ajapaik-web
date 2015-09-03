from django.contrib.auth.models import User
from django.db.models import Model, CharField, SmallIntegerField, BooleanField, ForeignKey, IntegerField, \
    DateTimeField, TextField, ImageField, URLField, ManyToManyField, OneToOneField
from django.db.models.signals import post_save

from project.utils import calculate_thumbnail_size
from project.common.models import BaseSource


class Source(BaseSource):
    pass

class CatProfile(Model):
    user = OneToOneField(User, primary_key=True)

    class Meta:
        db_table = 'project_catprofile'


def _user_post_save(sender, instance, **kwargs):
    CatProfile.objects.get_or_create(user=instance)


post_save.connect(_user_post_save, sender=User)

class CatTag(Model):
    name = CharField(max_length=255, unique=True)
    level = SmallIntegerField(blank=True, null=True)
    active = BooleanField(default=True)

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        db_table = 'project_cattag'


class CatRealTag(Model):
    name = CharField(max_length=255, unique=True)

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        db_table = 'project_catrealtag'


class CatAppliedTag(Model):
    tag = ForeignKey('CatRealTag')
    photo = ForeignKey('CatPhoto')

    class Meta:
        db_table = 'project_catappliedtag'


class CatTagPhoto(Model):
    tag = ForeignKey('CatTag')
    album = ForeignKey('CatAlbum')
    photo = ForeignKey('CatPhoto')
    profile = ForeignKey('CatProfile', related_name='tags')
    value = IntegerField(db_index=True)
    source = CharField(max_length=3, default='mob')
    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s - %s - %s - %s - %s' % (self.photo, self.tag, self.value, self.profile, self.source)

    class Meta:
        db_table = 'project_cattagphoto'


class CatUserFavorite(Model):
    album = ForeignKey('CatAlbum')
    photo = ForeignKey('CatPhoto')
    profile = ForeignKey('CatProfile')
    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('album', 'photo', 'profile'),)
        db_table = 'project_catuserfavorite'

    def __unicode__(self):
        return u'%s - %s - %s' % (self.album, self.photo, self.profile)


class CatPhoto(Model):
    title = CharField(max_length=255)
    description = TextField(null=True, blank=True)
    height = IntegerField(null=True, blank=True)
    width = IntegerField(null=True, blank=True)
    image = ImageField(upload_to='cat', max_length=255, height_field='height', width_field='width')
    author = CharField(max_length=255, null=True, blank=True)
    source = ForeignKey('Source', null=True, blank=True)
    source_url = URLField(null=True, blank=True, max_length=255)
    source_key = CharField(max_length=255, blank=True, null=True)
    tags = ManyToManyField(CatTag, related_name='photos', through=CatTagPhoto)
    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_catphoto'

    def __unicode__(self):
        return u'%s' % self.title

    def get_source_with_key(self):
        if self.source_key:
            return str(self.source.description + ' ' + self.source_key)
        return self.source.name

    # FIXME: Ineffective
    def thumb_width(self):
        return calculate_thumbnail_size(self.width, self.height, 400)[0]

    def thumb_height(self):
        return calculate_thumbnail_size(self.width, self.height, 400)[1]


class CatAlbum(Model):
    title = CharField(max_length=255)
    subtitle = CharField(max_length=255)
    image = ImageField(upload_to='cat', max_length=255)
    photos = ManyToManyField(CatPhoto, related_name='album')
    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s' % self.title

    class Meta:
        db_table = 'project_catalbum'


class CatPushDevice(Model):
    profile = ForeignKey('CatProfile')
    type = CharField(max_length=254)
    token = CharField(max_length=254)
    filter = CharField(max_length=1000, null=True, blank=True)

    class Meta:
        db_table = 'project_catpushdevice'
