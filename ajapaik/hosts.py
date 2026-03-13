from django_hosts import patterns, host

host_patterns = patterns(
    '',
    host(r'www', 'ajapaik.ajapaik.urls', name='www'),
)
