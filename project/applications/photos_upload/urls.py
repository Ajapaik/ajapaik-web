from django.conf.urls import url

from . import views


urlpatterns = [
    url('^photos/$', views.MainView.as_view(), name='mass-photo-upload-main'),
]
