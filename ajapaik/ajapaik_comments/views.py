import django_comments
from django.conf import settings
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.views import View
from django_comments.models import CommentFlag
from django_comments.signals import comment_was_flagged
from django_comments.views.comments import post_comment

from ajapaik.ajapaik.models import Photo
from ajapaik.ajapaik_comments.forms import EditCommentForm
from ajapaik.ajapaik_comments.utils import get_comment_replies


def get_comment_like_count(request, comment_id):
    comment = get_object_or_404(
        django_comments.get_model(), pk=comment_id, site__pk=settings.SITE_ID
    )

    return JsonResponse({
        'like_count': comment.like_count(),
        'dislike_count': comment.dislike_count()
    })


class CommentList(View):
    '''Render comment list. Only comment that not marked as deleted should be shown.'''
    template_name = 'comments/list.html'
    comment_model = django_comments.get_model()
    form_class = django_comments.get_form()

    def _aggregate_comment_and_replies(self, comments, flat_comment_list):
        '''Recursively build comments and their replies list.'''
        for comment in comments:
            flat_comment_list.append(comment)
            subcomments = get_comment_replies(comment).filter(
                is_removed=False
            ).order_by('submit_date')
            self._aggregate_comment_and_replies(
                comments=subcomments, flat_comment_list=flat_comment_list
            )

    def get(self, request, photo_id):
        flat_comment_list = []
        # Selecting photo's top level comments(pk == parent_id) and that has
        # been not removed.
        comments = self.comment_model.objects.filter(
            object_pk=photo_id, parent_id=F('pk'), is_removed=False
        ).order_by('submit_date')
        self._aggregate_comment_and_replies(
            comments=comments, flat_comment_list=flat_comment_list
        )
        content = render_to_string(
            template_name=self.template_name,
            request=request,
            context={
                'comment_list': flat_comment_list,
                'reply_form': self.form_class(get_object_or_404(
                    Photo, pk=photo_id)),
            }
        )
        comments_count = len(flat_comment_list)
        return JsonResponse({
            'content': content,
            'comments_count': comments_count,
        })


class PostComment(View):
    form_class = django_comments.get_form()

    def post(self, request, photo_id):
        form = self.form_class(
            target_object=get_object_or_404(Photo, pk=photo_id),
            data=request.POST
        )
        if form.is_valid():
            response = post_comment(request)
            if response.status_code != 302:
                return JsonResponse({
                    'comment': [_('Sorry but we fail to post your comment.')]
                })
        return JsonResponse(form.errors)


class EditComment(View):
    form_class = django_comments.get_form()

    def post(self, request):
        form = EditCommentForm(request.POST)
        if form.is_valid() and form.comment.user == request.user:
            form.comment.comment = form.cleaned_data['text']
            form.comment.save()
        return JsonResponse(form.errors)


class DeleteComment(View):
    comment_model = django_comments.get_model()

    def _perform_delete(self, request, comment):
        flag, created = CommentFlag.objects.get_or_create(
            comment_id=comment.pk,
            user=request.user,
            flag=CommentFlag.MODERATOR_DELETION
        )
        comment.is_removed = True
        comment.save()
        comment_was_flagged.send(
            sender=comment.__class__,
            comment=comment,
            flag=flag,
            created=created,
            request=request,
        )

    def post(self, request):
        comment_id = request.POST.get('comment_id')
        if comment_id:
            comment = get_object_or_404(self.comment_model, pk=comment_id)
            if comment.user == request.user:
                replies = get_comment_replies(comment)
                self._perform_delete(request, comment)
                for reply in replies:
                    self._perform_delete(request, reply)
        return JsonResponse({
            'status': 200
        })
