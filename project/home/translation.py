from modeltranslation.translator import translator, TranslationOptions
from project.home.models import Photo, Area, Album, CatAlbum


class PhotoTranslationOptions(TranslationOptions):
    fields = ('title', 'description',)

class AreaTranslationOptions(TranslationOptions):
    fields = ('name',)

class AlbumTranslationOptions(TranslationOptions):
    fields = ('name',)

class CatAlbumTranslationOptions(TranslationOptions):
    fields = ('title', 'subtitle')

translator.register(Photo, PhotoTranslationOptions)
translator.register(Area, AreaTranslationOptions)
translator.register(Album, AlbumTranslationOptions)
translator.register(CatAlbum, CatAlbumTranslationOptions)