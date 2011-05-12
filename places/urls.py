# Import django modules
from django.conf.urls.defaults import *


urlpatterns = patterns('places.views',
    url(r'^$', 'index', name='waypoints-index'),
    url(r'^gr/(?P<id>\w{5})/$', 'gr', name='gr'),
    url(r'^gr/new/$', 'gr_new', name='gr-new'),
    url(r'^save$', 'save', name='waypoints-save'),
    url(r'^search$', 'search', name='waypoints-search'),
    url(r'^query$', 'place', name='waypoints-query'),
    url(r'^upload$', 'upload', name='waypoints-upload'),
)
