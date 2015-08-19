from haystack import indexes
from project.home.models import Photo


class PhotoIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    description_et = indexes.CharField(model_attr='description_et', null=True)
    description_fi = indexes.CharField(model_attr='description_fi', null=True)
    description_sv = indexes.CharField(model_attr='description_sv', null=True)
    description_nl = indexes.CharField(model_attr='description_nl', null=True)
    description_de = indexes.CharField(model_attr='description_de', null=True)
    description_ru = indexes.CharField(model_attr='description_ru', null=True)
    description_en = indexes.CharField(model_attr='description_et', null=True)
    author = indexes.CharField(model_attr='author', null=True)
    types = indexes.CharField(model_attr='types', null=True)
    source = indexes.CharField(model_attr='source__description', null=True)
    source_key = indexes.CharField(model_attr='source_key', null=True)
    address = indexes.CharField(model_attr='address', null=True)

    def get_model(self):
        return Photo

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(rephoto_of__isnull=True)