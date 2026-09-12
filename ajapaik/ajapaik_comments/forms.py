from django import forms
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django_comments import get_model


class EditCommentForm(forms.Form):
    comment_id = forms.IntegerField()
    text = forms.CharField()

    def clean_comment_id(self):
        self.comment = get_object_or_404(
            get_model(), pk=self.cleaned_data['comment_id']
        )

    def clean(self):
        if self.comment.comment == self.cleaned_data['text']:
            forms.ValidationError(_('Nothing to change.'), code='same_text')
