import logging
import argparse
from StationsDataSetBuilder import StationsDataSetBuilder

if __name__ == '__main__':
    # Args
    ap = argparse.ArgumentParser()
    ap.add_argument('--input-file', required=True)
    ap.add_argument('--radius', required=True)
    ap.add_argument('--output-file', required=False)
    args = ap.parse_args()
    # Log
    logging.basicConfig(filename='find-a-manor.log', filemode='a', format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S', level=logging.DEBUG)        
    # Go!
    print(f'filtering stations to those [{args.radius}km] from origin')    
    sdb = StationsDataSetBuilder.from_file(args.input_file)
    sdb.filter_stations_to_radius(int(args.radius))
    print(f'\t[{sdb.count()}] stations left') 
    sdb.write(args.output_file if args.output_file is not None else args.input_file)
