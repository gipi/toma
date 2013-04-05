# Import django modules
from django.http import HttpResponse, \
        HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.contrib.gis.geos import Point
from django.contrib.gis.gdal import DataSource
from django.core.exceptions import ObjectDoesNotExist
# Import system modules
import simplejson
import itertools
import tempfile
import os
from PIL import Image, ImageFont, ImageDraw
# The urlparse module is renamed to urllib.parse in Python 3.0.
# The 2to3 tool will automatically adapt imports when converting your sources to 3.0.
from urlparse import urlparse

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

def get_gr_and_user_or_bad_response(request):
    """
    https://docs.djangoproject.com/en/dev/topics/http/views/#the-403-http-forbidden-view

    http://chronosbox.org/blog/manipulando-erros-http-403-permissao-negada-no-django?lang=en
    """
    try:
        referer = request.META['HTTP_REFERER']
    except KeyError:
        return None, None

    pieces = urlparse(referer)[2].split('/')

    if pieces[1] != "gr":
        return None, None

    # check if geo-room and user exist
    try:
        gr, gruser = get_room_and_user(pieces[2], request.session.session_key)
    except ObjectDoesNotExist:
        return None, None

    return gr, gruser

def gr(request, id):
    """
    Geo-Room: shows a group of users on the map
    updating their position.

    The Geo-Room MUST be created with the gr_new.

    Check if the user is already present in this georoom
    otherwise register inside it.
    """
    gr = get_object_or_404(GeoRoom, idx=id)
    gruser, created = GRUser.objects.get_or_create(
            session_key=request.session.session_key,
        )

    gr.users.add(gruser)

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

    gr, gruser = get_gr_and_user_or_bad_response(request)
    if gr is None:
        return HttpResponseBadRequest()

    data = simplejson.loads(request.raw_post_data)

    gruser.name = data["name"]
    gruser.save()

    return HttpResponse(simplejson.dumps(dict(response=0)),
            mimetype="application/json")

@csrf_exempt
def gr_set_position(request):
    """
    Set the position of the user with the given session_key
    """
    gr, gruser = get_gr_and_user_or_bad_response(request)
    try:
        position = request.POST['position']
    except KeyError:
        return HttpResponseBadRequest()

    p = position.split(":")

    place = GRPlace.objects.create(user=gruser, position=Point(float(p[0]), float(p[1])))

    return HttpResponse(simplejson.dumps(dict(response=0)),
            mimetype="application/json")

# decorator?
def get_room_and_user(gr_id, session_key):
    # check if geo-room and user exist
    gr = GeoRoom.objects.get(idx=gr_id)
    gruser = GRUser.objects.get(session_key=session_key)

    return gr, gruser

@csrf_exempt
def gr_get_users(request):
    """
    Returns in a JSON the users in this GeoRoom and their position.

    The GeoRoom is taken by the HTTP_REFERER and a check is done
    if the user associated with the session_key is allowed to
    be informed about that GeoRoom.
    """
    try:
        referer = request.META['HTTP_REFERER']
    except KeyError:
        return HttpResponseBadRequest()

    pieces = urlparse(referer)[2].split('/')

    if pieces[1] != "gr":
        return HttpResponseBadRequest()

    # check if geo-room and user exist
    try:
        gr, gruser = get_room_and_user(pieces[2], request.session.session_key)
    except ObjectDoesNotExist:
        return HttpResponseBadRequest()

    # get all the users in this georoom excluding the user doing the request
    grusers = gr.users.all().exclude(pk=gruser.pk)

    users = [{"name": x.name, "lat": x.grplace_set.all()[0].position.x, "lng": x.grplace_set.all()[0].position.y}
            for x in grusers
                if len(x.grplace_set.all()) > 0]


    return HttpResponse(simplejson.dumps(users), mimetype="application/json")

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

    gr_id = "".join(id)

    # TODO: check if exists yet
    gr = GeoRoom(idx=gr_id)
    gr.save()

    return HttpResponseRedirect(reverse('gr', args=[gr_id]))

def gr_marker(request, name):
    """
    Create a marker with the user name
    """
    try:
        font = ImageFont.truetype(settings.STATIC_ROOT + "/font.otf", 15)
    except ImportError:
        font = ImageFont.load_default()

    response = HttpResponse(mimetype='image/png')
    base = Image.open(settings.STATIC_ROOT + "/base_marker.png")

    draw = ImageDraw.Draw(base)
    tw, th = draw.textsize(name)
    iw, ih = base.size

    draw.text((iw/2 - tw/2,ih/3 - th/2), name, font=font, fill=(0,0,0))

    base.save(response, "png")

    return response

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
