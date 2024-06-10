from GoogleMapsAdapter import GoogleMapsAdapter
from geopy import distance
import json
import logging

class StationsDataSetBuilder:
    def __init__(self, origin, stations : list[dict]):
        self.gma = GoogleMapsAdapter()        
        self._logger = logging.getLogger(__name__).getChild(__class__.__name__)        
        self.stations = stations
        self.origin = origin

    @classmethod
    def from_file(cls, filepath):
        with open(filepath, 'r') as input_json:
            data = json.load(input_json)
        return cls(data['origin'], data['stations'])

    def count(self):
        return len(self.stations)

    def set_distances(self):
        for station in self.stations:
            if 'geometry' in station:
                logging.debug(f'calculating distance for [{self.origin["name"]}] to [{station['name']}] ')
                station['distance_km'] = distance.distance((self.origin['geometry']['latitude'], self.origin['geometry']['longitude']), (station['geometry']['latitude'], station['geometry']['longitude'])).kilometers     
                self._logger.debug(f'\tgot distance of [{station['distance_km']} kilometers]')

    def set_travel_times_from_place_id(self):
        for station in self.stations:
            if 'travel_time_secs' in station:
                self.logger.debug(f'- station [{station['name']}] already has travel times set, skipping')
                continue            
            self._logger.debug(f'attempting to get travel time to [{station['name']}]')
            if (time_secs := self.gma.get_journey_time_from_place_id(self.origin['place_id'], station['place_id'])) is not None:
                self._logger.debug(f'\tgot travel time of {time_secs} seconds')
                station['travel_time_secs'] = time_secs
                station['travel_time_mins'] = time_secs / 60
            else:
                print(f'- Unable to get travel time for [{station['name']}]')
                self._logger.debug(f'\tunable to get travel time for [{station['name']}]')

    def set_travel_times_from_coords(self):
        for station in self.stations:
            if 'travel_time_secs' in station:
                self.logger.debug(f'- station [{station['name']}] already has travel times set, skipping')                
                continue
            self._logger.debug(f'attempting to get travel time for [{self.origin['name']}]')
            if (time_secs := self.gma.get_journey_time_from_coords((self.origin['geometry']['latitude'],self.origin['geometry']['longitude']), (station['geometry']['latitude'],station['geometry']['longitude']))) is not None:
                self._logger.debug(f'\tgot travel time of {time_secs} seconds')
                station['travel_time_secs'] = time_secs
                station['travel_time_mins'] = time_secs / 60
            else:
                print(f'- Unable to get travel time for [{station['name']}]')                
                self._logger.debug(f'\tunable to get travel time for [{station['name']}]')                

    def set_google_place_id(self):
        for station in self.stations:
            place_id = self.gma.get_place_id(station['geometry']['latitude'], station['geometry']['longitude'])
            if place_id is not None:
                station['place_id'] = place_id
            else:
                print(f'\t- No place_id returned for station {station["name"]}')
                logging.debug(f'no place_id returned for station {station["name"]}')

    def filter_stations_to_radius(self, radius_km):
        self.stations = [station for station in self.stations if ('distance_km' in station and station['distance_km'] <= radius_km) or ('distance_km' not in station)]

    def filter_stations_to_travel_time(self, time_secs):
        self.stations = [station for station in self.stations if ('travel_time_secs' in station and station['travel_time_secs'] <= time_secs) or ('travel_time_secs' not in station)]    

    def write(self, file):
        json_out = { 
                        'count': len(self.stations),
                        'origin': self.origin,
                        'stations': self.stations 
                    }
        with open(file, 'w', encoding='utf-8') as fout:
            json.dump(json_out, fout, ensure_ascii=False, indent=4)