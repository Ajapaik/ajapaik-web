from modeltranslation.translator import translator, TranslationOptions
from project.sift.models import CatAlbum


class CatAlbumTranslationOptions(TranslationOptions):
    fields = ('title', 'subtitle')


translator.register(CatAlbum, CatAlbumTranslationOptions)
