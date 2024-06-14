import logging
import argparse
from StationsDataSetBuilder import StationsDataSetBuilder

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input-file', required=True)
    ap.add_argument('--travel-time-secs', required=True)
    ap.add_argument('--operator', required=True)
    ap.add_argument('--output-file', required=False)
    return ap.parse_args()

if __name__ == '__main__':
    logging.basicConfig(filename='find-a-manor.log', filemode='a', format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S', level=logging.DEBUG)            
    args = parse_args()
    # Go!
    sdb = StationsDataSetBuilder.from_file(args.input_file)
    if args.operator == 'lte':
        print(f'- Filtering stations to those equal to or less than [{args.travel_time_secs} seconds] from origin')    
        sdb.filter_stations_to_travel_time_lte(int(args.travel_time_secs))
    elif args.operator == 'gte':
        print(f'- Filtering stations to those equal to or less than [{args.travel_time_secs} seconds] from origin')    
        sdb.filter_stations_to_travel_time_gte(int(args.travel_time_secs))
    else:
        print(f'error: incorrect operator value, must be ''gte'' or ''lte''.')
        exit(1)

    print(f'[{sdb.count()}] stations left') 
    sdb.write(args.output_file if args.output_file is not None else args.input_file)
