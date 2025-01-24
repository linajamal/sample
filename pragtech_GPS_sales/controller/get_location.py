from odoo import http
from odoo.http import request
import json
import requests

class GetLocationController(http.Controller):
    @http.route('/update-driver-location', type='json', auth='public', csrf=False)
    def update_drivers_live_location(self, **kwargs):
        if request.session.uid:
            res_users = request.env['res.users'].sudo().search([('id', '=', request.env.user.id)])
            res_partner = request.env['res.partner'].sudo().search([('id', '=', res_users.partner_id.id)])
            
            lat = request.dispatcher.jsonrequest.get('lat')
            lng = request.dispatcher.jsonrequest.get('lng')
                        
            if lat and lng:
                res_partner.sudo().write({
                    'latitude': lat,
                    'longitude': lng,
                })
                
                address = self.get_address_from_latlng(lat, lng)
                if address:
                    res_partner.sudo().write({
                        'street': address.get('street', ''),
                        'city': address.get('city', ''),
                        'state_id': self.get_state_id(address.get('state_id', '')),
                        'zip': address.get('zip', ''),
                        'country_id': self.get_country_id(address.get('country_id', ''))
                    })
                    return {'status': 'success', 'message': 'Location and address updated successfully'}

                return {'status': 'error', 'message': 'Unable to retrieve address'}
            
            return {'status': 'error', 'message': 'Invalid location data'}

        return {'status': 'error', 'message': 'User not logged in'}
    
    def get_address_from_latlng(self, latitude, longitude):
        google_maps_api_key = request.env['ir.config_parameter'].sudo().get_param('google_maps_api_token')
        geocode_url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={google_maps_api_key}'
        try:
            response = requests.get(geocode_url)
            data = response.json()
            if data['status'] == 'OK':
                # Extract address components
                address_components = data['results'][0]['address_components']
                address = {
                    'street': '',
                    'city': '',
                    'state_id': None,
                    'country_id': None
                }

                for component in address_components:
                    if 'route' in component['types']:
                        address['street'] = component['long_name']
                    elif 'locality' in component['types']:
                        address['city'] = component['long_name']
                    elif 'administrative_area_level_1' in component['types']:
                        address['state_id'] = component['long_name']
                    elif 'country' in component['types']:
                        address['country_id'] = component['long_name']
                return address
            else:
                return None
        except Exception as e:
            return None

    def get_state_id(self, state_name):
        """Get the state ID by name from the database"""
        if state_name:
            state = request.env['res.country.state'].sudo().search([('name', '=', state_name)], limit=1)
            if state:
                return state.id
        return False

    def get_country_id(self, country_name):
        """Get the country ID by name from the database"""
        if country_name:
            country = request.env['res.country'].sudo().search([('name', '=', country_name)], limit=1)
            if country:
                return country.id
        return False
