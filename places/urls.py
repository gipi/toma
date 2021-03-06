# Import django modules
from django.conf.urls import *


urlpatterns = patterns('places.views',
    url(r'^$', 'index', name='waypoints-index'),
    url(r'^gr/users/$', 'gr_get_users', name='gr-users'),
    url(r'^gr/position/$', 'gr_set_position', name='gr-position'),
    url(r'^gr/(?P<id>\w{5})/$', 'gr', name='gr'),
    url(r'^gr/marker/(?P<name>\w+)\.png$', 'gr_marker', name='gr-marker'),
    url(r'^gr/name/$', 'gr_set_name', name='gr-set-name'),
    url(r'^gr/new/$', 'gr_new', name='gr-new'),
    url(r'^save$', 'save', name='waypoints-save'),
    url(r'^search$', 'search', name='waypoints-search'),
    url(r'^query$', 'place', name='waypoints-query'),
    url(r'^upload$', 'upload', name='waypoints-upload'),
)
