from django_hosts import host, patterns

host_patterns = patterns(
    "",
    host(r"www", "ajapaik.ajapaik.urls", name="www"),
)
