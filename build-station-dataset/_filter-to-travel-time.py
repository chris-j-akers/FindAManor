import logging
import argparse
from StationsDataSetBuilder import StationsDataSetBuilder

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input-file', required=True)
    ap.add_argument('--travel-time-secs', required=True)
    ap.add_argument('--output-file', required=False)
    return ap.parse_args()

if __name__ == '__main__':
    logging.basicConfig(filename='find-a-manor.log', filemode='a', format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S', level=logging.DEBUG)            
    args = parse_args()
    # Go!
    sdb = StationsDataSetBuilder.from_file(args.input_file)    
    print(f'- Filtering stations to those equal to or less than [{args.travel_time_secs} seconds] from origin')    
    sdb.filter_stations_to_travel_time(int(args.travel_time_secs))
    print(f'[{sdb.count()}] stations left') 
    sdb.write(args.output_file if args.output_file is not None else args.input_file)
