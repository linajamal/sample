odoo.define('pragtech_GPS_sales.get_location', [], function (require) {
    "use strict";
    console.log('---------------js_loading');
    function updateLocation() {
        // Check if geolocation is available
        console.log('---------------navigator', navigator);
        console.log('---------------navigator.geolocation', navigator.geolocation);
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function (position) {
                // Get latitude and longitude
                var lat = position.coords.latitude;
                var lng = position.coords.longitude;
                console.log('----------lat', lat)
                console.log('----------lng', lng)
                // Prepare the data to send to the backend
                var locationData = {
                    lat: lat,
                    lng: lng,
                };

                $.ajax({
                    url: '/update-driver-location',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({
                        'lat': locationData.lat,
                        'lng': locationData.lng
                    }),
                    success: function (response) {
                        console.log('Location updated successfully:', response);
                    },
                    error: function (error) {
                        console.error('Error updating location:', error);
                    }
                });
                
            }, function (error) {
                console.error('Error getting location:', error);
            });
        } else {
            console.error('Geolocation is not supported by this browser.');
        }
    }

    // Trigger location update every 5 seconds
    setInterval(updateLocation, 5000);

    console.log('---------------js_loading2');
});
