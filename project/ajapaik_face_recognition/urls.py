from django.conf.urls import url

from project.ajapaik_face_recognition import views

urlpatterns = [
    url(r'^add-subject/$', views.add_subject, name='face_recognition_add_subject'),
    url(r'^add-rectangle/$', views.add_rectangle, name='face_recognition_add_rectangle'),
    url(r'^get-rectangles/(?P<photo_id>\d+)/$', views.get_rectangles, name='face_recognition_get_rectangles'),
    url(r'^add-rectangle-feedback/$', views.add_rectangle_feedback, name='face_recognition_add_rectangle_feedback'),
    url(r'^guess-subject-form/(?P<rectangle_id>\d+)/$', views.get_guess_form_html, name='face_recognition_guess_subject_form'),
    url(r'^guess-subject/$', views.guess_subject, name='face_recognition_guess_subject'),
]
