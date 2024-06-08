import logging
from pykml import parser

class StationFileAdapter:
    def get_stations(self):
        raise NotImplementedError

class TrainlineStationFileAdapter(StationFileAdapter):
    FILE_COL_NAME=1
    FILE_COL_LATITUDE=5
    FILE_COL_LONGITUDE=6
    FILE_COL_COUNTRY=8
    
    def __init__(self, filepath):
        self._logger = logging.getLogger(__name__).getChild(__class__.__name__)
        self._separator = ';'
        self.filepath = filepath

    def get_stations(self):
        with open(self.filepath, 'r') as stations:
            stations =[
                        {   
                            'name': fields[self.FILE_COL_NAME], 
                            'geometry' : {
                                    'latitude': fields[self.FILE_COL_LATITUDE], 
                                    'longitude': fields[self.FILE_COL_LONGITUDE] 
                            }
                        } 
                        for fields in [ station.split(self._separator) for station in stations ] if fields[self.FILE_COL_COUNTRY] == 'GB']
        
            return stations

class TFLFileAdapter(StationFileAdapter):
    FILE_COL_LONGITUDE=0
    FILE_COL_LATITUDE=1     

    def __init__(self, filepath):
        self._logger = logging.getLogger(__name__).getChild(__class__.__name__)
        self._separator = ','
        self.filepath = filepath

    def get_stations(self):      
        with open(self.filepath) as kml:
            root = parser.parse(kml).getroot()
        stations = [ 
                        { 
                            'name': place.name.text.lstrip().rstrip(), 
                            'geometry': {
                                'latitude': place.Point.coordinates.text.split(',')[self.FILE_COL_LATITUDE].rstrip().lstrip(), 
                                'longitude': place.Point.coordinates.text.split(',')[self.FILE_COL_LONGITUDE].rstrip().lstrip() 
                            }
                        } 
                        for place in root.Document.Placemark 
                    ]
        
        return stations