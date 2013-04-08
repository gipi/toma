var ajax = require('forbeslindesay-ajax');

ajax({
    'complete': function() {
        console.log('position sent');
    },
    'error': function(xhr, textStatus, errorThrown) {
        console.log('error: ' + textStatus);
    }
});

var gHandleY = 0;
var isOpened = false;
var gMarker = new Array();

// http://stackoverflow.com/questions/442404/dynamically-retrieve-html-element-x-y-position-with-javascript
function getOffset( el ) {
    var _x = 0;
    var _y = 0;
    while( el && !isNaN( el.offsetLeft ) && !isNaN( el.offsetTop ) ) {
        _x += el.offsetLeft - el.scrollLeft;
        _y += el.offsetTop - el.scrollTop;
        el = el.offsetParent;
    }
    return { top: _y, left: _x };
}

function initialize() {
    var latlng = new google.maps.LatLng(-34.397, 150.644);
    var myOptions = {
        zoom: 15,
        center: latlng,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    var map = new google.maps.Map(
            document.getElementById("map_canvas"),
            myOptions);

    function addMarker(map, location, name) {
        var marker = new google.maps.Marker({
            position: location,
            title: "Hello World!",
            icon: "/gr/marker/" + name + ".png"
        });

        // To add the marker to the map, call setMap();
        marker.setMap(map);

        // add also a info window
        var contentString = new Date().toGMTString();
        var infowindow = new google.maps.InfoWindow({
            content: contentString
        });
        //infowindow.open(map, marker);

        return marker;
    }
    if (navigator.geolocation) {
        browserSupportFlag = true;

        var watchID = navigator.geolocation.watchPosition(
                function(position) {
                    var latLng = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
                    addMarker(map, latLng, "Me");
                    map.setCenter(latLng);
                    ajax.post(
                        '/gr/position/',
                        "position="+position.coords.latitude+":"+position.coords.longitude);
                }, function(err) {alert("Error: " + err)}, {
            enableHighAccuracy: true,
            maximumAge: 30000,
            timeout: 27000
        });
    } else {
        alert("Mi dispiace, il tuo browser non supporta la geolocalizzazione");
    }
    gHandleY = getOffset(document.getElementById('handle')).top;
    setInterval(function() {
            ajax.getJSON(
                '/gr/users/',
                function(r) {
                    var count = gMarker.length;
                    for (var cycle = 0 ; cycle < count ; cycle++) {
                        gMarker[cycle].setMap(null);
                    }

                    gMarker = new Array();

                    jr = r;
                    var count = jr.length;
                    for (var cycle = 0 ; cycle < count ; cycle++) {
                        gMarker.push(addMarker(map,new google.maps.LatLng(jr[cycle]["lat"], jr[cycle]["lng"]),jr[cycle]["name"]));
                    }
                });
    }, 15000);
}
function handleHandle() {
        window.scrollTo(0, isOpened ? 0 : gHandleY);
        isOpened = !isOpened;
}
function setName() {
    input = document.getElementById('name_input');
    ajax.post('/gr/name/', '{"name": "' + input.value + '"}');
}

