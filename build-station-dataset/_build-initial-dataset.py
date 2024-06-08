import logging
import argparse
import json
from StationFileAdapters import TFLFileAdapter, TrainlineStationFileAdapter
from StationsDataSetBuilder import StationsDataSetBuilder

if __name__ == '__main__':
    # Args
    ap = argparse.ArgumentParser()
    ap.add_argument('--origin-file', required=True)
    ap.add_argument('--output-file', required=True)
    args = ap.parse_args()
    # Log
    logging.basicConfig(filename='find-a-manor.log', filemode='a', format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S', level=logging.DEBUG)        
    # File parsers
    print(f'building station file adapters')
    tfl_file = TFLFileAdapter('./station-data/tfl-stations.kml')
    trainline_file = TrainlineStationFileAdapter('./station-data/uk-stations.csv')
    # Build initial list of all stations
    print(f'building dataset object')
    with open(args.origin_file, 'r') as origin_file:
        origin = json.load(origin_file)
    stations = StationsDataSetBuilder(origin, tfl_file.get_stations() + trainline_file.get_stations())
    print(f'\t[{stations.count()}] stations found')
    # Add distance to all stations from origin
    print(f'setting distances from origin [{origin["name"]}, {origin["geometry"]["latitude"]}, {origin["geometry"]["longitude"]}, {origin["place_id"]}]')
    stations.set_distances()
    # Save list to specified file
    print(f'writing to file [{args.output_file}]')
    stations.write(args.output_file)
