"""
Application urls.
"""
from django.conf.urls import url

from . import api, views

urlpatterns = [
    url('^upload/photos/$', views.MainView.as_view()),
    url('^api/v2/upload/photos/$', api.PhotoMassiveUpload.as_view()),
]
