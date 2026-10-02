from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _

from ajapaik.ajapaik.models import Album, AlbumPhoto, Licence, Photo
from ajapaik.ajapaik_upload.forms import (
    UserPhotoUploadAddAlbumForm,
    UserPhotoUploadForm,
)


def user_upload(request):
    context = {
        "ajapaik_facebook_link": settings.AJAPAIK_FACEBOOK_LINK,
        "is_user_upload": True,
        "show_albums_error": False,
    }

    if request.method == "POST":
        form = UserPhotoUploadForm(request.POST, request.FILES)
        albums = request.POST.getlist("albums")
        profile = request.get_user().profile

        if form.is_valid() and albums and len(albums) > 0:
            photo = form.save(commit=False)
            photo.user = profile

            if photo.uploader_is_author:
                photo.author = profile.get_display_name
                photo.licence = Licence.objects.get(id=17)  # CC BY 4.0

            photo.save()
            photo.set_aspect_ratio()
            photo.find_similar()
            albums = request.POST.getlist("albums")
            target_albums = list(Album.objects.filter(id__in=albums))
            album_photos = [
                AlbumPhoto(
                    photo=photo,
                    album=album,
                    type=AlbumPhoto.UPLOADED,
                    profile=profile,
                )
                for album in target_albums
            ]
            AlbumPhoto.objects.bulk_create(album_photos)

            for album in target_albums:
                album.set_calculated_fields()
                album.light_save()
            photo.add_to_source_album()

            if request.POST.get("geotag") == "true":
                return redirect(
                    f"{reverse('frontpage_photos')}?photo={photo.id!s}&locationToolsOpen=1"
                )
            else:
                context["message"] = _("Photo uploaded")

        if albums is None or len(albums) < 1:
            context["show_albums_error"] = True
    else:
        form = UserPhotoUploadForm()

    return render(request, "user_upload/user_upload.html", {**context, "form": form})


def user_upload_add_album(request):
    context = {"ajapaik_facebook_link": settings.AJAPAIK_FACEBOOK_LINK}
    profile = request.get_user().profile

    if request.method == "POST":
        form = UserPhotoUploadAddAlbumForm(request.POST, profile=profile)

        if form.is_valid():
            album = form.save(commit=False)
            album.profile = profile
            album.save()
            context["message"] = _("Album created")
    else:
        form = UserPhotoUploadAddAlbumForm(profile=profile)

    context["form"] = form

    return render(request, "user_upload/user_upload_add_album.html", context)


def photo_upload_modal(request, photo_id):
    photo = get_object_or_404(Photo, pk=photo_id)
    licence = Licence.objects.get(id=17)  # CC BY 4.0
    context = {
        "photo": photo,
        "licence": licence,
        "next": request.META.get("HTTP_REFERER"),
    }
    return render(request, "rephoto_upload/_rephoto_upload_modal_content.html", context)
