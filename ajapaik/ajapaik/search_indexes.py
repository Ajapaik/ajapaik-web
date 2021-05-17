from haystack import indexes

from ajapaik.ajapaik.models import Photo, Album


class PhotoIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)
    description_et = indexes.CharField(model_attr='description_et', null=True)
    description_lv = indexes.CharField(model_attr='description_lv', null=True)
    description_lt = indexes.CharField(model_attr='description_lt', null=True)
    description_fi = indexes.CharField(model_attr='description_fi', null=True)
    description_sv = indexes.CharField(model_attr='description_sv', null=True)
    description_nl = indexes.CharField(model_attr='description_nl', null=True)
    description_de = indexes.CharField(model_attr='description_de', null=True)
    description_ru = indexes.CharField(model_attr='description_ru', null=True)
    description_en = indexes.CharField(model_attr='description_en', null=True)
    title_et = indexes.CharField(model_attr='title_et', null=True)
    title_lv = indexes.CharField(model_attr='title_lv', null=True)
    title_lt = indexes.CharField(model_attr='title_lt', null=True)
    title_fi = indexes.CharField(model_attr='title_fi', null=True)
    title_sv = indexes.CharField(model_attr='title_sv', null=True)
    title_nl = indexes.CharField(model_attr='title_nl', null=True)
    title_de = indexes.CharField(model_attr='title_de', null=True)
    title_ru = indexes.CharField(model_attr='title_ru', null=True)
    title_en = indexes.CharField(model_attr='title_en', null=True)
    author = indexes.CharField(model_attr='author', null=True)
    types = indexes.CharField(model_attr='types', null=True)
    keywords = indexes.CharField(model_attr='keywords', null=True)
    source__description = indexes.CharField(model_attr='source__description', null=True)
    source_key = indexes.CharField(model_attr='source_key', null=True)
    address = indexes.CharField(model_attr='address', null=True)
    muis_title = indexes.CharField(model_attr='muis_title', null=True)
    muis_comment = indexes.CharField(model_attr='muis_comment', null=True)
    muis_event_description_set_note = indexes.CharField(model_attr='muis_event_description_set_note', null=True)
    muis_text_on_object = indexes.CharField(model_attr='muis_text_on_object', null=True)
    muis_legends_and_descriptions = indexes.CharField(model_attr='muis_legends_and_descriptions', null=True)

    def get_model(self):
        return Photo

    def index_queryset(self, using=None):
        return self.get_model().objects.all()


class AlbumIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)
    name_et = indexes.CharField(model_attr='name_et', null=True)
    name_lv = indexes.CharField(model_attr='name_lv', null=True)
    name_lt = indexes.CharField(model_attr='name_lt', null=True)
    name_fi = indexes.CharField(model_attr='name_fi', null=True)
    name_sv = indexes.CharField(model_attr='name_sv', null=True)
    name_nl = indexes.CharField(model_attr='name_nl', null=True)
    name_de = indexes.CharField(model_attr='name_de', null=True)
    name_ru = indexes.CharField(model_attr='name_ru', null=True)
    name_en = indexes.CharField(model_attr='name_en', null=True)

    def get_model(self):
        return Album

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(is_public=True, cover_photo__isnull=False,
                                               atype__in=[Album.CURATED, Album.PERSON])
