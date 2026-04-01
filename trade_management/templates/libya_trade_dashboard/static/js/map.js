var data = {}
    var count = 0
    var arr = []
    var status = false
    var markerMap

    function center() {

        navigator.geolocation.getCurrentPosition(function (position) {

            var latitude = position.coords.latitude
            var longitude = position.coords.longitude

            const map = new google.maps.Map(document.getElementById("map"), {
                zoom: 11,
                center: { lat: latitude, lng: longitude },
            });
            data.map = map
            google.maps.event.addListener(map, 'click', function (event) {

                if (count <= 0) {
                    arr.push([event.latLng.lat(), event.latLng.lng()])
                    placeMarker(event.latLng);
                    google.maps.event.addListener(markerMap, 'dragend', function (event) {
                        arr = []
                        arr.push([event.latLng.lat(), event.latLng.lng()])



            });
                }
                else {
                    arr = []
                    arr.push([event.latLng.lat(), event.latLng.lng()])
                    //reset the previous marker on the map
                     markerMap.setMap(null)
                     count = 0
                    //locate the new postion after the user click on the map agin
                    placeMarker(event.latLng)
                    // get the new postion after dragging the marker
        google.maps.event.addListener(markerMap, 'dragend', function (event) {
                        arr = []
                        arr.push([event.latLng.lat(), event.latLng.lng()])


            });

                }

            });
        })


        function placeMarker(location) {
            count++
            status = true
            var marker = new google.maps.Marker({
                position: location,
                draggable:true,
                map: data.map
            });
            markerMap = marker

        }

    }

center()
