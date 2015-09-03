from modeltranslation.translator import translator, TranslationOptions

from project.ajapaik.models import Photo, Area, Album


class PhotoTranslationOptions(TranslationOptions):
    fields = ('title', 'description',)


class AreaTranslationOptions(TranslationOptions):
    fields = ('name',)


class AlbumTranslationOptions(TranslationOptions):
    fields = ('name',)


translator.register(Photo, PhotoTranslationOptions)
translator.register(Area, AreaTranslationOptions)
translator.register(Album, AlbumTranslationOptions)
