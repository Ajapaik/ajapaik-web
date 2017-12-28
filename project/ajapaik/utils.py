from django.db.models import F
from django_comments import get_model

comment_model = get_model()


def get_comment_replies(comment):
    '''
    Returns queryset thet contain all reply for given comment.
    '''
    return comment_model.objects.filter(
        parent_id=comment.pk
    ).exclude(parent_id=F('pk'))