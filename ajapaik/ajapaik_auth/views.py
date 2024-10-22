from allauth.socialaccount.models import SocialApp, SocialToken
from django.http import HttpResponse
from django.shortcuts import render, redirect

from ajapaik.ajapaik.forms import OauthDoneForm


def login_modal(request):
    context = {
        'next': request.META.get('HTTP_REFERER', None),
        'type': request.GET.get('type', None)
    }
    return render(request, 'authentication/_login_modal_content.html', context)


def logout(request):
    from django.contrib.auth import logout

    logout(request)

    if 'HTTP_REFERER' in request.META:
        return redirect(request.META['HTTP_REFERER'])

    return redirect('/')


def oauthdone(request):
    user = request.user
    form = OauthDoneForm(request.GET)
    if form.is_valid():
        if user.is_anonymous:
            return HttpResponse('No user found', status=404)

        provider = form.cleaned_data['provider']
        allowed_providers = ['facebook', 'google', 'wikimedia-commons']
        if provider not in allowed_providers:
            return HttpResponse('Provider not in allowed providers.' + provider, status=404)

        app = SocialApp.objects.get_current(provider)

        if not app:
            return HttpResponse('Provider ' + provider + ' not found.', status=404)

        social_token = SocialToken.objects.get(account__user_id=user.id, app=app)
        if not social_token:
            return HttpResponse('Token not found.', status=404)

        token = social_token.token
        context = {
            'route': '/login',
            'provider': provider,
            'token': token
        }
        return render(request, 'socialaccount/oauthdone.html', context)

    return HttpResponse('No user found', status=404)
