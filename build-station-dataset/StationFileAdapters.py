import logging
from pykml import parser

class StationFileAdapter:
    def get_stations(self, set_station_suffix=True):
        raise NotImplementedError
    
    def set_station_suffix(self, place_name):
        station = place_name.split(' ')
        return place_name if station[-1] in ['station', 'Station'] else place_name + ' ' + 'Station'


class TrainlineStationFileAdapter(StationFileAdapter):
    def __init__(self, filepath):
        self._logger = logging.getLogger(__name__).getChild(__class__.__name__)
        self._separator = ';'
        self.filepath = filepath

    def get_stations(self, set_station_suffix=True):
        FILE_COL_NAME=1
        FILE_COL_LATITUDE=5
        FILE_COL_LONGITUDE=6
        FILE_COL_COUNTRY=8        
        with open(self.filepath, 'r') as stations:
            stations = [
                            {   
                                'name': self.set_station_suffix(fields[FILE_COL_NAME]) if set_station_suffix else fields[FILE_COL_NAME],
                                'type': 'national_rail',
                                'geometry' : {
                                    'latitude': fields[FILE_COL_LATITUDE], 
                                    'longitude': fields[FILE_COL_LONGITUDE] 
                                }
                            } 
                            for fields in [ station.split(self._separator) for station in stations ] if fields[FILE_COL_COUNTRY] == 'GB'
                        ]
            return stations


class TFLFileAdapter(StationFileAdapter):
    def __init__(self, kml_filepath, details_filepath):
        self._logger = logging.getLogger(__name__).getChild(__class__.__name__)
        self._separator = ','
        self.kml_filepath = kml_filepath
        self.kml_root = self._parse_kml_file()
        self.csv_filepath = details_filepath
        self.csv_data = self._parse_csv_file()        

    def _parse_kml_file(self):
        with open(self.kml_filepath) as kml:
            return parser.parse(kml).getroot()        

    def _parse_csv_file(self):
        with open(self.csv_filepath) as csv:
            return [line.split(',') for line in csv]

    def _match_station_name(self, kml_station_name, csv_station_name):
        if kml_station_name == csv_station_name:
            return True
        if (kml_split := kml_station_name.split(' '))[-1] in ['station', 'Station']:
            if ' '.join(kml_split[:-1]) == csv_station_name:
                return True
        return False

    def _get_fare_zone(self, kml_station_name):
        FILE_COL_NAME = 1
        FILE_COL_FAREZONE = 2
        # Really not very efficient, brute-force searching but I'm more interested in
        # getting this done - it doesn't need to be fast.
        for station in self.csv_data:
            if self._match_station_name(kml_station_name, station[FILE_COL_NAME]):
                return [station[FILE_COL_FAREZONE].split('|')]
        print(f'warning: no tfl fare-zone match for station [{kml_station_name}]')
        return None

    def get_stations(self, set_station_suffix=True):      
        KML_FILE_COL_LONGITUDE=0
        KML_FILE_COL_LATITUDE=1
        stations = [ 
                        { 
                            'name': self.set_station_suffix(place.name.text.lstrip().rstrip()) if set_station_suffix else place.name.text.lstrip().rstrip(),
                            'type': 'tfl',
                            'zone': self._get_fare_zone(place.name.text.lstrip().rstrip()),
                            'geometry': {
                                'latitude': place.Point.coordinates.text.split(',')[KML_FILE_COL_LATITUDE].rstrip().lstrip(), 
                                'longitude': place.Point.coordinates.text.split(',')[KML_FILE_COL_LONGITUDE].rstrip().lstrip() 
                            }
                        } 
                        for place in self.kml_root.Document.Placemark 
                    ]
        return stations