from django.forms import Form, CharField, BooleanField, IntegerField, TypedMultipleChoiceField


class NotValidatedMultipleChoiceField(TypedMultipleChoiceField):
    def to_python(self, value):
        return list(map(self.coerce, value))

    def validate(self, value):
        pass


class CuratorSearchForm(Form):
    fullSearch = CharField(max_length=255, required=False)
    useMUIS = BooleanField(initial=False, required=False)
    useDIGAR = BooleanField(initial=False, required=False)
    useMKA = BooleanField(initial=False, required=False)
    useETERA = BooleanField(initial=False, required=False)
    useFlickr = BooleanField(initial=False, required=False)
    useUTLIB = BooleanField(initial=False, required=False)
    useFinna = BooleanField(initial=False, required=False)
    useFotis = BooleanField(initial=False, required=False)
    # Also used for Finna and Fotis
    flickrPage = IntegerField(initial=1, required=False)
    filterExisting = BooleanField(initial=True, required=False)
    ids = NotValidatedMultipleChoiceField(coerce=str, required=False)
