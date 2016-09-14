from django.forms import Form, CharField, BooleanField, IntegerField, TypedMultipleChoiceField


class NotValidatedMultipleChoiceField(TypedMultipleChoiceField):
    def to_python(self, value):
        return map(self.coerce, value)

    def validate(self, value):
        pass


class CuratorSearchForm(Form):
    fullSearch = CharField(max_length=255, required=False)
    flickrPage = IntegerField(initial=1, required=False)
    filterExisting = BooleanField(initial=True, required=False)
    ids = NotValidatedMultipleChoiceField(coerce=str, required=False)
