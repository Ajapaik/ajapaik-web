from django.views.generic.base import TemplateView


class MainView(TemplateView):

    template_name = "photos_upload/main.html"
