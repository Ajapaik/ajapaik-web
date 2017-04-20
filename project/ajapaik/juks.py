import requests
from django import forms
from django.http import HttpResponse


class SiteForm(forms.Form):
    site = forms.CharField(max_length=50)


def empty_json(request):
    form = SiteForm(request.GET)
    if form.is_valid():
        url = 'http://juks.alkohol.ee/tools/vanalinnad/vector/places/' + form.cleaned_data['site'] + '/empty.json'
        response = requests.get(url)

        return HttpResponse(response)

    return HttpResponse({}, 400)


def layers(request):
    form = SiteForm(request.GET)
    if form.is_valid():
        url = 'http://juks.alkohol.ee/tools/vanalinnad/vector/places/' + form.cleaned_data['site'] + '/layers.xml'
        response = requests.get(url)

        return HttpResponse(response)

    return HttpResponse({}, 400)
