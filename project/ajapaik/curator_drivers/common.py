from django.forms import Form, CharField, BooleanField, IntegerField, TypedMultipleChoiceField


class NotValidatedMultipleChoiceField(TypedMultipleChoiceField):
    def to_python(self, value):
        return map(self.coerce, value)

    def validate(self, value):
        pass

class CuratorSearchForm(Form):
    fullSearch = CharField(max_length=255)
    useMUIS = BooleanField(initial=False, required=False)
    useDIGAR = BooleanField(initial=False, required=False)
    useETERA = BooleanField(initial=False, required=False)
    useFlickr = BooleanField(initial=False, required=False)
    filterExisting = BooleanField(initial=True, required=False)
    page = IntegerField(initial=1, required=False)
    ids = NotValidatedMultipleChoiceField(coerce=int, required=False)