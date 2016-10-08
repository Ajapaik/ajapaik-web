from modeltranslation.translator import translator, TranslationOptions

from project.ajapaik.models import Photo, Album, Licence


class PhotoTranslationOptions(TranslationOptions):
    fields = ('title', 'description',)


class AlbumTranslationOptions(TranslationOptions):
    fields = ('name',)


class LicenceTranslationOptions(TranslationOptions):
    fields = ('name',)


translator.register(Photo, PhotoTranslationOptions)
translator.register(Album, AlbumTranslationOptions)
translator.register(Licence, LicenceTranslationOptions)
