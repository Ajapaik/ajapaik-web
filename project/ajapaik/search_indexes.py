from haystack import indexes

from project.ajapaik.models import Photo, Album


class PhotoIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)
    description_en = indexes.CharField(model_attr='description_en', null=True)
    description_no = indexes.CharField(model_attr='description_no', null=True)
    author = indexes.CharField(model_attr='author', null=True)
    types = indexes.CharField(model_attr='types', null=True)
    keywords = indexes.CharField(model_attr='keywords', null=True)
    source = indexes.CharField(model_attr='source__description', null=True)
    source_key = indexes.CharField(model_attr='source_key', null=True)
    address = indexes.CharField(model_attr='address', null=True)

    def get_model(self):
        return Photo

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(rephoto_of__isnull=True)


class AlbumIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)
    name_en = indexes.CharField(model_attr='name_en', null=True)
    name_no = indexes.CharField(model_attr='name_no', null=True)

    def get_model(self):
        return Album

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(is_public=True)
