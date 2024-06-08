import json
import logging

from StationFileAdapters import TFLFileAdapter, TrainlineStationFileAdapter
from StationsDataSetBuilder import StationsDataSetBuilder
from Place import Place
from GoogleMapsAdapter import GoogleMapsAdapter

def dbg_print_json(json_data):
    json_formatted_str = json.dumps(json_data, indent=2)
    print(json_formatted_str)

def setup_logging(logfile='find-a-manor.log', filemode='w'):
    logging.basicConfig(filename=logfile, filemode=filemode, format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S', level=logging.DEBUG)

def main():
    setup_logging()

    # This could be passed as a parameter, but I'm not too fussed!
    # The co-ordinates and place_id can be taken from the maps websites.
    origin = Place('Sloane Square', 51.49237, 0.15604, 'ChIJ9033RhYFdkgR6i08EtbBeHk')

    tfl_file = TFLFileAdapter('./station-data/tfl-stations.kml')
    trainline_file = TrainlineStationFileAdapter('./station-data/uk-stations.csv')
    stations = StationsDataSetBuilder(tfl_file.get_stations() + trainline_file.get_stations())

    print(f'created initial stations DataSet with {stations.count()} stations.')

    # We have our origin and we have our initial DataSet of stations. Now we
    # use the geopy library to calculate the distances between our origin
    # and all the stations in that DataSet if they have geometry coordinates.
    # If they don't, we leave the station in and will populate it later using
    # Google maps API
    stations.set_distances(origin)    
    radius = 50

    # Filter out the stations that are outside our pre-defined radius. We don't
    # want to be commuting to Aberdeen everyday, so might as well remove it. 
    # This reduces the number of times we access google api which can
    # incur cost!
    stations.filter_to_stations_to_radius(radius)
    print(f'filtered to [{stations.count()}] stations within a [{radius}]km radius from [{origin.name}] where possible (note stations without distances available are also included)')

    # Google docs say the best way to use the distance matrix API is with 
    # place_ids, not co-ordinates :shrug:. Here, we'll iterate through all our
    # stations and see if we can find their place_id based on their co-ordinates.
    # If not, we print out the station so we can add them to the dataset manually
    # later (hopefully there's not too many!)
    stations.set_google_place_id()
    print(f'finished adding place ids')

    # Now add times to each train station
    print(f'setting travels times')
    stations.set_travel_times(origin)

    # Done! Just write our DataSet to a JSON file.
    print('done! now writing dataset to disk')
    stations.write('./stations.json')

if __name__ == '__main__':
       main()


