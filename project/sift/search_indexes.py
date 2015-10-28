from haystack import indexes
from project.sift.models import CatPhoto


class CatPhotoIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title', null=True)
    description = indexes.CharField(model_attr='description', null=True)
    author = indexes.CharField(model_attr='author', null=True)
    source = indexes.CharField(model_attr='source__description', null=True)
    source_key = indexes.CharField(model_attr='source_key', null=True)

    def get_model(self):
        return CatPhoto

    def index_queryset(self, using=None):
        return self.get_model().objects.all()