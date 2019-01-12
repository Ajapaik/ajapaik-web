# encoding: utf-8
from django.core.management.base import BaseCommand
from django.db.models import Q

from ajapaik.ajapaik.models import Profile


class Command(BaseCommand):
    help = 'Attach first and last name to profile directly'

    def handle(self, *args, **options):
        profiles_with_data = Profile.objects.filter(
            Q(fb_name__isnull=False) |
            Q(google_plus_name__isnull=False) |
            Q(user__first_name__isnull=False, user__last_name__isnull=False, user__last_name__ne='', user__first_name__ne='')
        )
        #print profiles_with_data.count()
        i = 1
        for each in profiles_with_data:
            #print i
            if each.fb_name:
                parts = each.fb_name.split(' ')
                each.first_name = parts[0]
                if len(parts) > 1:
                    each.last_name = parts[1]
            elif each.google_plus_name:
                parts = each.google_plus_name.split(' ')
                each.first_name = parts[0]
                if len(parts) > 1:
                    each.last_name = parts[1]
            elif each.user.first_name and each.user.last_name:
                each.first_name = each.user.first_name
                each.last_name = each.user.last_name
            each.save()
            i += 1