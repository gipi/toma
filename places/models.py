# Import django modules
from django.contrib.gis.db import models
from django.contrib.gis import admin

import settings


class GRUser(models.Model):
    """
    This contains the data for the user with active session
    in at least one geo room. It's not necessary to be logged
    in the site.

    http://yuji.wordpress.com/2008/05/14/django-attatching-arbitrary-data-to-anonymous-sessions/
    """
    name = models.CharField(max_length=10)
    session_key = models.CharField(max_length=40)

class GRPlace(models.Model):
    """
    This contains the position at given time of
    an user in the map.
    """
    user = models.ForeignKey(GRUser)
    position = models.PointField(srid=4326)
    time = models.DateTimeField(auto_now=True)

    objects = models.GeoManager()

class GeoRoom(models.Model):
    """
    Represents a group of users.
    """
    idx = models.CharField(max_length=settings.GEO_ROOM_ID_LENGTH)
    users = models.ManyToManyField(GRUser)

class Place(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField()
    geometry = models.PointField(srid=4326)
    objects = models.GeoManager()

    def __unicode__(self):
        return '%s %s %s' % (self.name, self.geometry.x, self.geometry.y)

############ ADMIN STUFFS #########################
# http://docs.djangoproject.com/en/1.3/ref/contrib/gis/tutorial/#osmgeoadmin-intro
class PlaceAdmin(admin.OSMGeoAdmin):
	default_lon = 855670.46847410582
	default_lat = 5632636.8934435854
	default_zoom = 14
	map_template = 'places/map_editing.html'

class GeoRoomAdmin(admin.ModelAdmin):
	list_display = ('idx', '_users_number')

	def _users_number(self, obj):
		return '%d' % len(obj.users.all())
	_users_number.short_description = '# users'


admin.site.register(Place, PlaceAdmin)
admin.site.register(GeoRoom, GeoRoomAdmin)
