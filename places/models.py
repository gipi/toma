# Import django modules
from django.contrib.gis.db import models
from django.contrib.gis import admin


class Place(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField()
    geometry = models.PointField(srid=4326)
    objects = models.GeoManager()

    def __unicode__(self):
        return '%s %s %s' % (self.name, self.geometry.x, self.geometry.y)

# http://docs.djangoproject.com/en/1.3/ref/contrib/gis/tutorial/#osmgeoadmin-intro
class PlaceAdmin(admin.OSMGeoAdmin):
	default_lon = 855670.46847410582
	default_lat = 5632636.8934435854
	default_zoom = 14
	map_template = 'places/map_editing.html'

admin.site.register(Place, PlaceAdmin)
