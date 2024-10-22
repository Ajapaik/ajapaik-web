from random import choice

from django.shortcuts import render
from django.utils.translation import gettext as _

from ajapaik.ajapaik.models import Supporter


def supporters(request, year=None):
    context = {}
    is_lang_et = request.LANGUAGE_CODE == 'et'

    supporters = {
        'Kulka': {
            'alternate_text': _('KulKa logo'),
            'url': 'https://www.kulka.ee/et' if is_lang_et else 'https://www.kulka.ee/en',
            'img': 'images/logo-kulka_et.png' if is_lang_et else 'images/logo-kulka.png',
        },
        'Ministry of Education': {
            'alternate_text': _('Ministry of Education logo'),
            'url': 'https://www.hm.ee/et' if is_lang_et else 'https://www.hm.ee/en',
            'img': 'images/logo-ministry-of-education-and-research_et.png' if is_lang_et
            else 'images/logo-ministry-of-education-and-research.png',
        },
        'EV100': {
            'alternate_text': _('EV100 logo'),
            'url': 'https://www.ev100.ee/et/ajapaik-selgitame-koos-valja-kuidas-eesti-kohad-aegade-jooksul-muutunud'
            if is_lang_et
            else 'https://www.ev100.ee/en/ajapaik-selgitame-koos-valja-kuidas-eesti-kohad-aegade-jooksul-muutunud',
            'img': 'images/ev100.png'
        },
        'National Foundation of Civil Society': {
            'alternate_text': _('KYSK logo'),
            'url': 'https://www.kysk.ee/est' if is_lang_et else 'https://www.kysk.ee/nfcs',
            'img': 'images/logo-kysk_et.png' if is_lang_et else 'images/logo-kysk.png'
        },
        'Ministry of Culture': {
            'alternate_text': _('Ministry of Culture'),
            'url': 'https://www.kul.ee/et' if is_lang_et else 'https://www.kul.ee/en',
            'img': 'images/logo-ministry-of-culture_et.png' if is_lang_et
            else 'images/logo-ministry-of-culture.png'
        },
        'Republic of Estonia National Heritage Board': {
            'alternate_text': _('Republic of Estonia National Heritage Board'),
            'url': 'https://www.muinsuskaitseamet.ee/et' if is_lang_et
            else 'https://www.muinsuskaitseamet.ee/en',
            'img': 'images/logo-estonian-national-heritage-board_et.png' if is_lang_et
            else 'images/logo-estonian-national-heritage-board.png'
        },
        'Year of Digital Culture 2020': {
            'alternate_text': _('Year of Digital Culture 2020'),
            'url': 'https://www.nlib.ee/et/digikultuur2020' if is_lang_et
            else 'https://www.nlib.ee/en/digikultuur2020',
            'img': 'images/logo-year-of-digital-culture-2020_et.png' if is_lang_et
            else 'images/logo-year-of-digital-culture-2020.png'
        },
        'Wikimedia Finland': {
            'alternate_text': _('Wikimedia Finland'),
            'url': 'https://wikimedia.fi/',
            'img': 'images/logo-wikimedia-finland.png'
        }

    }
    current_supporters = [
        supporters['Wikimedia Finland'],
    ]

    previous_supporters = [
        supporters['Kulka'],
        supporters['Ministry of Culture'],
        supporters['EV100'],
        supporters['Ministry of Education'],
        supporters['National Foundation of Civil Society'],
        supporters['Republic of Estonia National Heritage Board'],
        supporters['Kulka'],
        supporters['Year of Digital Culture 2020']
    ]

    supporters = Supporter.objects.all()

    context['current_supporters'] = current_supporters
    context['previous_supporters'] = previous_supporters
    context['supporters'] = supporters

    return render(request, 'donate/supporters.html', context)


def privacy(request):
    return render(request, 't&c/privacy.html')


def terms(request):
    return render(request, 't&c/terms.html')


def donate(request):
    pictures = [
        {
            'image_url': 'https://ajapaik.ee//media/uploads/2016/08/07/muis_eU4vJ5H.jpg',
            'resource_url': 'https://ajapaik.ee/photo/82938/'
        },
        {
            'image_url': 'https://ajapaik.ee//media/uploads/2017/03/27/muis_5dtkncr.jpg',
            'resource_url': 'https://ajapaik.ee/photo/111092'
        },
        {
            'image_url': 'https://ajapaik.ee/media/uploads/2016/10/10/muis_YHWUAey.jpg',
            'resource_url': 'https://ajapaik.ee/photo/89376'
        }
    ]
    context = {
        'is_donate': True,
        'picture': choice(pictures)
    }

    return render(request, 'donate/donate.html', context)
