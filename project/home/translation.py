from modeltranslation.translator import translator, TranslationOptions
from project.home.models import Photo, Area


class PhotoTranslationOptions(TranslationOptions):
    fields = ('title', 'description',)

class AreaTranslationOptions(TranslationOptions):
    fields = ('name',)

translator.register(Photo, PhotoTranslationOptions)
translator.register(Area, AreaTranslationOptions)