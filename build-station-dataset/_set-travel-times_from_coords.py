import logging
import argparse
from StationsDataSetBuilder import StationsDataSetBuilder

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input-file', required=True)
    ap.add_argument('--output-file', required=False)
    return ap.parse_args()    

if __name__ == '__main__':
    if input('This command uses the Google Maps Distance Matrix API which can incur cost. Are you sure you want to continue? Y/N: ') not in ['Y','y']:
        exit(0)    
    args = parse_args()
    logging.basicConfig(filename='find-a-manor.log', filemode='a', format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S', level=logging.DEBUG)        
    # Go!
    sdb = StationsDataSetBuilder.from_file(args.input_file)
    sdb.set_travel_times_from_coords()
    sdb.write(args.output_file if args.output_file is not None else args.input_file)
