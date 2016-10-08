from modeltranslation.translator import translator, TranslationOptions

from project.ajapaik.models import Photo, Album, Licence, Municipality, County, Country


class PhotoTranslationOptions(TranslationOptions):
    fields = ('title', 'description',)


class AlbumTranslationOptions(TranslationOptions):
    fields = ('name',)


class LicenceTranslationOptions(TranslationOptions):
    fields = ('name',)


class CountryTranslationOptions(TranslationOptions):
    fields = ('name',)


class CountyTranslationOptions(TranslationOptions):
    fields = ('name',)


class MunicipalityTranslationOptions(TranslationOptions):
    fields = ('name',)


translator.register(Photo, PhotoTranslationOptions)
translator.register(Album, AlbumTranslationOptions)
translator.register(Licence, LicenceTranslationOptions)
translator.register(Country, CountryTranslationOptions)
translator.register(County, CountyTranslationOptions)
translator.register(Municipality, MunicipalityTranslationOptions)
