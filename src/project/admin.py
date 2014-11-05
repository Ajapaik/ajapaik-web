from django.conf.urls import patterns, url
from django.contrib import admin
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from functools import update_wrapper
from project.models import  Photo, GeoTag, \
                            Profile, Source, \
                            Skip, Action, \
                            Album, City, CSVPhoto

from sorl.thumbnail.admin import AdminImageMixin


class CSVUploadAdmin(admin.ModelAdmin):
	pass
	#Example of self-made view
	# @permission_required('blog.add_post')
	# def admin_my_view(request, model_admin):
	# 	opts = model_admin.model._meta
	# 	admin_site = model_admin.admin_site
	# 	has_perm = request.user.has_perm(opts.app_label + '.' \
	# 	                                 + opts.get_change_permission())
	# 	context = {
	# 		'admin_site': admin_site.name,
	# 		'title': "My Custom View",
	# 		'opts': opts,
	# 		'root_path': '/%s' % admin_site.root_path,
	# 		'app_label': opts.app_label,
	# 		'has_change_permission': has_perm
	# 	}
	#
	#
	# 	template = 'admin/demo_app/admin_my_view.html'
	# 	return render_to_response(template, context,context_instance=RequestContext(request))


class PhotoAdmin(AdminImageMixin, admin.ModelAdmin):
	@staticmethod
	def _distance_between_two_points_on_sphere(lon_1, lat_1, lon_2, lat_2):
		import math

		rad = math.pi / 180.0
		equatorial_radius_meters = 6378137
		lon_1_rad = lon_1 * rad
		lat_1_rad = lat_1 * rad
		lon_2_rad = lon_2 * rad
		lat_2_rad = lat_2 * rad
		cos_angle = math.sin(lat_1_rad) * math.sin(lat_2_rad) + math.cos(lat_1_rad) * math.cos(lat_2_rad) * math.cos(
			lon_2_rad - lon_1_rad)

		if cos_angle >= 1:
			return 0

		angle = math.acos(cos_angle)
		return angle * equatorial_radius_meters


	def save_model(self, request, obj, form, change):
		if obj.lat and obj.lon and obj.bounding_circle_radius:
			# If an administrator sets a bounding circle, invalidate GeoTags outside of it
			all_photo_geo_tags = GeoTag.objects.filter(photo_id=obj.id)
			for geo_tag in all_photo_geo_tags:
				if self._distance_between_two_points_on_sphere(obj.lon, obj.lat, geo_tag.lon,
				                                               geo_tag.lat) > obj.bounding_circle_radius:
					geo_tag.is_correct = False
				else:
					geo_tag.is_correct = True
				geo_tag.save()
		obj.save()

admin.site.register(Photo, PhotoAdmin)
admin.site.register(GeoTag)
admin.site.register(Profile)
admin.site.register(Source)
admin.site.register(Skip)
admin.site.register(Action)
admin.site.register(Album)
admin.site.register(City)
admin.site.register(CSVPhoto, CSVUploadAdmin)