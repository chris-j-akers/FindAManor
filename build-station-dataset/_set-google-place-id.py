import logging
import argparse
from StationsDataSetBuilder import StationsDataSetBuilder

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input-file', required=True)
    ap.add_argument('--output-file', required=False)
    return ap.parse_args()

if __name__ == '__main__':
    if input('This command uses the Google Maps Geo Matrix API which can incur cost. Are you sure you want to continue? Y/N: ') not in ['Y','y']:
        exit(0)        
    logging.basicConfig(filename='find-a-manor.log', filemode='a', format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S', level=logging.DEBUG)        
    args = parse_args()
    # Go!
    sdb = StationsDataSetBuilder.from_file(args.input_file)
    print(f'- Trying to find google place id for [{sdb.count()}] stations')
    sdb.set_google_place_id()
    sdb.write(args.output_file if args.output_file is not None else args.input_file)
