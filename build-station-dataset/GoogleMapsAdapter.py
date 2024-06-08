import logging
import requests
import json

class GoogleMapsAdapter:

    def __init__(self):
        self._logger = logging.getLogger(__name__).getChild(__class__.__name__)
        with open('../.env/google_api_key', 'r') as api_keyfile:
            self.api_key = api_keyfile.readline().rstrip()
        self._logger.debug(f'got api-key [{self.api_key}] from file')

    def _get_default_headers(self):
        return {'Content-Type': 'application/json', 
                'X-Goog-Api-Key': f'{self.api_key}'}

    def _format_json(self, json_data):
        return json.dumps(json_data, indent=2)

    def get_journey_time_from_place_id(self, origin_place_id , destination_place_id):
        URL='https://maps.googleapis.com/maps/api/distancematrix/json?mode=transit&transit_mode=rail&units=kilometers&origins={0}&destinations={1}&key=' + self.api_key
        response_json = requests.get(URL.format(f'place_id:{origin_place_id}', f'place_id:{destination_place_id}')).json()
        if (response_json['rows'][0]['elements'][0]['status'] == 'OK'):
            self._logger.debug(f'{self._format_json(response_json)}')            
            return response_json['rows'][0]['elements'][0]['duration']['value']
        else:
            return None        
        
    def get_place_id(self, latitude, longitude):
        URL = 'https://maps.googleapis.com/maps/api/geocode/json?latlng={0},{1}&key=' + self.api_key
        self._logger.debug(f'calling {URL.format(latitude, longitude)}')
        response_json = requests.get(URL.format(latitude, longitude)).json()
        if (response_json['status']) == 'OK':
            self._logger.debug(f'{self._format_json(response_json)}')
            place_id = response_json['results'][0]['place_id']
            return place_id
        else:
            self._logger.debug(f'no value for returned')
            return None            
