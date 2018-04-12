def move_user_data(old_user, new_user):
    is_old_user_dummy = hasattr(old_user, 'is_dummy') and old_user.is_dummy
    if not is_old_user_dummy or not old_user.is_active:
        # User is normal user(not dummy) so data moving is not required. Or
        # user already was processed and marked as inactive.
        return

    # Ajapaik specific data.
    new_user.profile.photos.add(*old_user.profile.photos.all())
    new_user.profile.albums.add(*old_user.profile.albums.all())
    new_user.profile.album_photo_links.add(*old_user.profile.album_photo_links.all())
    new_user.profile.datings.add(*old_user.profile.datings.all())
    new_user.profile.dating_confirmations.add(*old_user.profile.dating_confirmations.all())
    new_user.profile.difficulty_feedbacks.add(*old_user.profile.difficulty_feedbacks.all())
    new_user.profile.geotags.add(*old_user.profile.geotags.all())
    new_user.profile.points.add(*old_user.profile.points.all())
    new_user.profile.skips.add(*old_user.profile.skips.all())
    new_user.profile.likes.add(*old_user.profile.likes.all())
    new_user.profile.tour_groups.add(*old_user.profile.tour_groups.all())
    new_user.profile.owned_tours.add(*old_user.profile.owned_tours.all())
    new_user.profile.tour_rephotos.add(*old_user.profile.tour_rephotos.all())
    new_user.profile.tour_views.add(*old_user.profile.tour_views.all())

    # Other user data.
    new_user.comment_comments.add(*old_user.comment_comments.all())
