import os
import argparse
import json
from StationsDataSetBuilder import StationsDataSetBuilder

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input-file', required=True)
    ap.add_argument('--output-file', required=False)
    return ap.parse_args()

def parse_json_file(file_path):
    with open(file_path, 'r') as json_file:
        json_data = json.load(json_file)
    return json_data

def write_csv(filename, json_data):
    with open(filename, 'w', encoding='utf-8') as csv_file:
        csv_file.write('Name,Latitude,Longitude,Type,Zone,Description\n')
        for station in json_data['stations']:
            csv_file.write(f'{station['name']},{station['geometry']['latitude']},{station['geometry']['longitude']},{station['type']},{'|'.join([str(zone) for zone in station['zone']]) if 'zone' in station else ''},{station['name']} [{str(round(station['travel_time_mins']))} mins]\n')

if __name__ == '__main__':
    args = parse_args()
    json_data = parse_json_file(args.input_file)
    write_csv(args.output_file if args.output_file is not None else os.path.dirname(args.input_file) + '/' + os.path.basename(args.input_file).split('.')[0] + '.csv', json_data)
    print('done')
