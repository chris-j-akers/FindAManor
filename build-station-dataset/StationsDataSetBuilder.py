from GoogleMapsAdapter import GoogleMapsAdapter
from geopy import distance
from Place import Place
import json
import logging

class StationsDataSetBuilder:
    def __init__(self, stations : list[dict]):
        self._logger = logging.getLogger(__name__).getChild(__class__.__name__)        
        self.gma = GoogleMapsAdapter()
        self.stations = stations

    def count(self):
        return len(self.stations)

    def set_distances(self, starting_point : Place):
        for station in self.stations:
            if 'geometry' in station:
                logging.debug(f'calculating distance for [{starting_point.name}] to [{station['name']}] ')
                station['distance_km'] = distance.distance((starting_point.latitude, starting_point.longitude), (station['geometry']['latitude'], station['geometry']['longitude'])).kilometers     
                self._logger.debug(f'\tgot distance of [{station['distance_km']} kilometers]')

    def set_travel_times(self, starting_point : Place):
        for station in self.stations:
            self._logger.debug(f'attempting to get travel time for [{starting_point['name']}]')
            if (time_secs := self.gma.get_journey_time(starting_point, Place(name=station['name'], latitude=station['geometry']['latitude'], longitude=station['geometry']['longitude'], place_id=station['place_id']))) is not None:
                self._logger.debug(f'\tgot travel time of {time_secs} seconds')
                station['travel_time_secs'] = time_secs
                station['travel_time_mins'] = time_secs / 60
            else:
                self._logger.debug(f'\tunable to get travel time for [{station['name']}]')

    def set_google_place_id(self):
        for station in self.stations:
            place_id = self.gma.get_place_id(station['geometry']['latitude'], station['geometry']['longitude'])
            if place_id is not None:
                station['place_id'] = place_id
            else:
                print(f'no geo data returned for station {station["name"]}')
                logging.debug(f'no geo data returned for station {station["name"]}')

    def filter_to_stations_to_radius(self, radius_km):
        self.stations = [station for station in self.stations if ('distance_km' in station and station['distance_km'] <= radius_km) or ('distance_km' not in station)]

    def write(self, file):
        with open(file, 'w', encoding='utf-8') as fout:
            json.dump(self.stations, fout, ensure_ascii=False, indent=4)