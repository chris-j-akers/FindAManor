import logging
import argparse
import json
from StationFileAdapters import TFLFileAdapter, TrainlineStationFileAdapter
from StationsDataSetBuilder import StationsDataSetBuilder

def parse_origin_file(file_path):
    with open(file_path, 'r') as origin_file:
        origin = json.load(origin_file)
    return origin

def initialise_dataset(origin_file, trainline_filepath, tfl_kml_filepath, tfl_csv_filepath, no_tfl=False):
    tfl_file = TFLFileAdapter(tfl_kml_filepath, tfl_csv_filepath)
    trainline_file=TrainlineStationFileAdapter(trainline_filepath)
    origin = parse_origin_file(origin_file)
    stations = StationsDataSetBuilder(origin, trainline_file.get_stations() if no_tfl else tfl_file.get_stations() + trainline_file.get_stations())
    print(f'[{stations.count()}] stations found')
    return stations

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--origin-file', required=True)
    ap.add_argument('--output-file', required=True)
    ap.add_argument('--no-tfl', required=False, default=False)
    return ap.parse_args()

if __name__ == '__main__':
    logging.basicConfig(filename='find-a-manor.log', filemode='a', format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S', level=logging.DEBUG)            
    args = parse_args()
    print('- Initialising stations dataset')
    stations = initialise_dataset(args.origin_file, tfl_kml_filepath='./station-data/tfl/tfl-stations.kml', tfl_csv_filepath='./station-data/tfl/tfl-stations.csv', trainline_filepath='./station-data/national-rail/uk-stations.csv', no_tfl=args.no_tfl)
    print(f'- Setting distances from origin')
    stations.set_distances()
    print(f'- Writing to file [{args.output_file}]')
    stations.write(args.output_file)
