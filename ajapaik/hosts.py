from django.conf import settings
from django_hosts import patterns, host
host_patterns = patterns(
    '',
    host(r'www', 'ajapaik.ajapaik.urls', name='www'),
    host(r'opendata', 'ajapaik.ajapaik.urls_opendata', name='opendata'),
)