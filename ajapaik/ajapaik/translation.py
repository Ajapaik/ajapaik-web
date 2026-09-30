from modeltranslation.translator import TranslationOptions, translator

from ajapaik.ajapaik.models import Album, Area, Licence, Photo


class PhotoTranslationOptions(TranslationOptions):
    fields = (
        "title",
        "description",
    )


class AreaTranslationOptions(TranslationOptions):
    fields = ("name",)


class AlbumTranslationOptions(TranslationOptions):
    fields = ("name",)


class LicenceTranslationOptions(TranslationOptions):
    fields = ("name",)


translator.register(Photo, PhotoTranslationOptions)
translator.register(Area, AreaTranslationOptions)
translator.register(Album, AlbumTranslationOptions)
translator.register(Licence, LicenceTranslationOptions)
