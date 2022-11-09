from modeltranslation.translator import translator, TranslationOptions

from ajapaik.ajapaik.models import Photo, Area, Album, Licence, PhotoSearchIndex,SearchIndexModel,AlbumSearchIndex


class PhotoSearchIndexTranslationOptions(TranslationOptions):
    fields = ('text',)

class AlbumSearchIndexTranslationOptions(TranslationOptions):
    fields = ('text',)

class PhotoTranslationOptions(TranslationOptions):
    fields = ('title', 'description',)


class AreaTranslationOptions(TranslationOptions):
    fields = ('name',)


class AlbumTranslationOptions(TranslationOptions):
    fields = ('name',)


class LicenceTranslationOptions(TranslationOptions):
    fields = ('name',)


translator.register(PhotoSearchIndex, PhotoSearchIndexTranslationOptions)
translator.register(AlbumSearchIndex, AlbumSearchIndexTranslationOptions)
translator.register(Photo, PhotoTranslationOptions)
translator.register(Area, AreaTranslationOptions)
translator.register(Album, AlbumTranslationOptions)
translator.register(Licence, LicenceTranslationOptions)
