from django.db.models import Model, CharField, TextField, DateTimeField


class BaseSource(Model):
    name = CharField(max_length=255)
    description = TextField(null=True, blank=True)
    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True
        db_table = 'project_source'