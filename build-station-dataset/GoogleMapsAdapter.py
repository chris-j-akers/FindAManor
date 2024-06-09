import logging
import requests
import json
import datetime

class GoogleMapsAdapter:

    def __init__(self):
        self._logger = logging.getLogger(__name__).getChild(__class__.__name__)
        with open('../.env/google_api_key', 'r') as api_keyfile:
            self.api_key = api_keyfile.readline().rstrip()
        self._logger.debug(f'got api-key [{self.api_key}] from file')

    def _get_next_weekday_as_secs_from_epoch(self, date=datetime.date.today()):
        next_weekday_date = date + datetime.timedelta(days=-date.isoweekday() + 8) if date.isoweekday() in set((6, 7)) else date
        next_weekday_datetime = datetime.datetime(next_weekday_date.year, next_weekday_date.month, next_weekday_date.day, 17, 45, 0)
        return int(next_weekday_datetime.timestamp())

    def _get_default_headers(self):
        return {'Content-Type': 'application/json', 
                'X-Goog-Api-Key': f'{self.api_key}'}

    def _format_json(self, json_data):
        return json.dumps(json_data, indent=2)

    def get_journey_time_from_place_id(self, origin_place_id , destination_place_id):
        URL='https://maps.googleapis.com/maps/api/distancematrix/json?mode=transit&transit_mode=rail&units=kilometers&origins={0}&destinations={1}&departure_time={2}&key=' + self.api_key
        response_json = requests.get(URL.format(f'place_id:{origin_place_id}', f'place_id:{destination_place_id}', self._get_next_weekday_as_secs_from_epoch())).json()
        if (response_json['rows'][0]['elements'][0]['status'] == 'OK'):
            self._logger.debug(f'{self._format_json(response_json)}')            
            return response_json['rows'][0]['elements'][0]['duration']['value']
        else:
            self._logger.debug(f'unable to get data for origin: [{origin_place_id}], destination: [{destination_place_id}], response is:')
            self._logger.debug(f'{self._format_json(response_json)}')            
            return None
        
    def get_journey_time_from_coords(self, origin_coords, destination_coords):
        URL='https://maps.googleapis.com/maps/api/distancematrix/json?mode=transit&transit_mode=rail&units=kilometers&origins={0}&destinations={1}&departure_time={2}&key=' + self.api_key
        response_json = requests.get(URL.format(f'{origin_coords[0]},{origin_coords[1]}', f'{destination_coords[0]},{destination_coords[1]}', self._get_next_weekday_as_secs_from_epoch())).json()
        if (response_json['rows'][0]['elements'][0]['status'] == 'OK'):
            self._logger.debug(f'{self._format_json(response_json)}')            
            return response_json['rows'][0]['elements'][0]['duration']['value']
        else:
            self._logger.debug(f'unable to get data for co-ordinates {destination_coords}, response is: ')
            self._logger.debug(f'{self._format_json(response_json)}')
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
            self._logger.debug(f'no place_id available in response:')
            self._logger.debug(f'{self._format_json(response_json)}')
            return None            
