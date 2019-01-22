from haystack import indexes

from ajapaik.ajapaik.models import Photo, Album


class PhotoIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)
    description_et = indexes.CharField(model_attr='description_et', null=True)
    description_fi = indexes.CharField(model_attr='description_fi', null=True)
    description_sv = indexes.CharField(model_attr='description_sv', null=True)
    description_nl = indexes.CharField(model_attr='description_nl', null=True)
    description_de = indexes.CharField(model_attr='description_de', null=True)
    description_ru = indexes.CharField(model_attr='description_ru', null=True)
    description_en = indexes.CharField(model_attr='description_et', null=True)
    author = indexes.CharField(model_attr='author', null=True)
    types = indexes.CharField(model_attr='types', null=True)
    keywords = indexes.CharField(model_attr='keywords', null=True)
    source = indexes.CharField(model_attr='source__description', null=True)
    source_key = indexes.CharField(model_attr='source_key', null=True)
    address = indexes.CharField(model_attr='address', null=True)
    people = indexes.MultiValueField()

    def get_model(self):
        return Photo

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

    def prepare_people(self, obj):
        return [subject.name for subject in obj.people.all()]


class AlbumIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)
    name_et = indexes.CharField(model_attr='name_et', null=True)
    name_fi = indexes.CharField(model_attr='name_fi', null=True)
    name_sv = indexes.CharField(model_attr='name_sv', null=True)
    name_nl = indexes.CharField(model_attr='name_nl', null=True)
    name_de = indexes.CharField(model_attr='name_de', null=True)
    name_ru = indexes.CharField(model_attr='name_ru', null=True)
    name_en = indexes.CharField(model_attr='name_en', null=True)
    # created = indexes.DateTimeField(model_attr='created', null=False)
    # cover_photo = indexes.CharField(model_attr='cover_photo', null=True)
    # cover_photo_width = indexes.IntegerField(model_attr='cover_photo__width', null=True)
    # cover_photo_height = indexes.IntegerField(model_attr='cover_photo__height', null=True)

    def get_model(self):
        return Album

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(is_public=True, cover_photo__isnull=False,
                                               atype__in=[Album.CURATED, Album.PERSON])
