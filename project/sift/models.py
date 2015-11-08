from autoslug import AutoSlugField
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Model, CharField, SmallIntegerField, BooleanField, ForeignKey, IntegerField, \
    DateTimeField, TextField, ImageField, URLField, ManyToManyField, OneToOneField, NullBooleanField
from django.db.models.signals import post_save

from project.utils import calculate_thumbnail_size
from project.common.models import BaseSource


class Source(BaseSource):
    pass


class CatProfile(Model):
    user = OneToOneField(User, primary_key=True)

    class Meta:
        db_table = 'project_catprofile'

    @property
    def id(self):
        return self.user_id


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
    photo = ForeignKey('CatPhoto', related_name='applied_tags')

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
    slug = AutoSlugField(populate_from='title', always_update=True)
    description = TextField(null=True, blank=True)
    height = IntegerField(null=True, blank=True)
    width = IntegerField(null=True, blank=True)
    image = ImageField(upload_to='cat', max_length=255, height_field='height', width_field='width')
    author = CharField(max_length=255, null=True, blank=True)
    source = ForeignKey('Source', null=True, blank=True)
    source_url = URLField(null=True, blank=True, max_length=255)
    source_key = CharField(max_length=255, blank=True, null=True)
    muis_id = CharField(max_length=100, null=True, blank=True)
    muis_media_id = CharField(max_length=100, null=True, blank=True)
    tags = ManyToManyField(CatTag, related_name='photos', through=CatTagPhoto)
    flip = NullBooleanField()
    invert = NullBooleanField()
    stereo = NullBooleanField()
    rotated = IntegerField(null=True, blank=True)
    date_text = CharField(max_length=255, null=True, blank=True)
    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_catphoto'

    def __unicode__(self):
        return u'%s' % self.title

    def get_source_with_key(self):
        if self.source_key:
            return self.source.description + ' ' + str(self.source_key)
        return self.source.name

    # FIXME: Ineffective
    def thumb_width(self):
        return calculate_thumbnail_size(self.width, self.height, 400)[0]

    def thumb_height(self):
        return calculate_thumbnail_size(self.width, self.height, 400)[1]


class CatAlbum(Model):
    title = CharField(max_length=255)
    subtitle = CharField(max_length=255)
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


class CatPhotoPair(Model):
    profile = ForeignKey('CatProfile')
    photo1 = ForeignKey('CatPhoto', related_name='pair_first')
    photo2 = ForeignKey('CatPhoto', related_name='pair_second')
    comment = TextField(blank=True, null=True)
    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_catphotopair'

    def get_sbs_url(self, is_fb_share=0):
        return reverse('project.sift.views.cat_side_by_side_image', args=(self.pk, is_fb_share))

    def get_absolute_url(self):
        return reverse('project.sift.views.cat_connection_permalink', args=(self.pk,))
