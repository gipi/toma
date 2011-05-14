# Import django modules
from django.http import HttpResponse, \
        HttpResponseRedirect, HttpResponseNotAllowed
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.contrib.gis.geos import Point
from django.contrib.gis.gdal import DataSource
# Import system modules
import simplejson
import itertools
import tempfile
import os
# Import custom modules
from .models import Place, GRUser, GRPlace, GeoRoom
import settings


def index(request):
    'Display map'
    waypoints = Place.objects.order_by('name')
    return render_to_response('places/index.html', {
        'waypoints': waypoints,
        'content': render_to_string('places/waypoints.html', {'waypoints': waypoints}),
    }, context_instance=RequestContext(request))



def gr(request, id):
    """
    Geo-Room: shows a group of users on the map
    updating their position.
    """
    return render_to_response(
        'places/gr.html',
        {},
        context_instance=RequestContext(request))

@csrf_exempt
def gr_set_name(request):
    """
    Set the name of the user with the given session_key.
    """
    if request.method == "GET":
        return HttpResponseNotAllowed(['POST'])

    # FIXME: understand if this is a security problem
    data = simplejson.loads(request.raw_post_data)

    gruser, created = GRUser.objects.get_or_create(
            session_key=request.session.session_key,
        )
    gruser.name = data["name"]
    gruser.save()

    return HttpResponse(simplejson.dumps(dict(response=0)),
            mimetype="application/json")

def gr_new(request):
    """
    Create a new geo room with a new available code
    and redirect to that.
    """
    import random
    choices = "abcdefghilmnopqrstuvzABCDEFGHILMNOPQRST1234567890"

    id = []
    for i in range(settings.GEO_ROOM_ID_LENGTH):
        id.append(random.choice(choices))

    return HttpResponseRedirect(reverse('gr', args=["".join(id)]))

def save(request):
    'Save waypoints'
    for waypointString in request.POST.get('waypointsPayload', '').splitlines():
        waypointID, waypointX, waypointY = waypointString.split()
        waypoint = Place.objects.get(id=int(waypointID))
        waypoint.geometry.set_x(float(waypointX))
        waypoint.geometry.set_y(float(waypointY))
        waypoint.save()
    return HttpResponse(simplejson.dumps(dict(isOk=1)), mimetype='application/json')

def search(request):
    'Search waypoints'
    # Build searchPoint
    try:
        searchPoint = Point(float(request.GET.get('lng')), float(request.GET.get('lat')))
    except:
        return HttpResponse(simplejson.dumps(dict(isOk=0, message='Could not parse search point')))
    # Search database
    waypoints = Place.objects.distance(searchPoint).order_by('distance')
    # Return
    return HttpResponse(simplejson.dumps(dict(
        isOk=1,
        content=render_to_string('places/waypoints.html', {
            'waypoints': waypoints
        }),
        waypointByID=dict((x.id, {
            'name': x.name,
            'lat': x.geometry.y,
            'lng': x.geometry.x,
        }) for x in waypoints),
    )), mimetype='application/json')

def place(request):
    """
    Return the 900913 coordinates for the given address.
    Principally used to obtain the coords for a given address
    to centre the map with.
    """
    import geopy
    from django.contrib.gis.geos import GEOSGeometry

    places = geopy.geocoders.Google().geocode(request.GET.get('address'), exactly_one=False)

    dplaces = {}
    for p in places:
        P = 'POINT(' + str(p[1][1]) + ' ' + str(p[1][0]) + ')'
        # SRID 4326 is the common latitude/longitude coords
        pnt = GEOSGeometry(P, srid=4326)
        pnt.transform(900913)
        dplaces[p[0]] = pnt

    return HttpResponse(simplejson.dumps(dict(
        (key, {
            'lat': value.x,
            'lng': value.y,
        }) for key, value in dplaces.iteritems())
    ), mimetype='application/json')


def upload(request):
    'Upload waypoints'
    # If the form contains an upload,
    if 'gpx' in request.FILES:
        # Get
        gpxFile = request.FILES['gpx']
        # Save
        targetPath = tempfile.mkstemp()[1]
        destination = open(targetPath, 'wt')
        for chunk in gpxFile.chunks():
            destination.write(chunk)
        destination.close()
        # Parse
        dataSource = DataSource(targetPath)
        layer = dataSource[0]
        waypointNames = layer.get_fields('name')
        waypointGeometries = layer.get_geoms()
        for waypointName, waypointGeometry in itertools.izip(waypointNames, waypointGeometries):
            waypoint = Place(name=waypointName, geometry=waypointGeometry.wkt)
            waypoint.save()
        # Clean up
        os.remove(targetPath)
    # Redirect
    return HttpResponseRedirect(reverse('waypoints-index'))
