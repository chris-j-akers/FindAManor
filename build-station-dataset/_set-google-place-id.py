import logging
import argparse
from StationsDataSetBuilder import StationsDataSetBuilder

if __name__ == '__main__':
    # Args
    ap = argparse.ArgumentParser()
    ap.add_argument('--input-file', required=True)
    ap.add_argument('--output-file', required=False)
    args = ap.parse_args()
    # Log
    logging.basicConfig(filename='find-a-manor.log', filemode='a', format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S', level=logging.DEBUG)        
    # Go!
    sdb = StationsDataSetBuilder.from_file(args.input_file)
    sdb.set_google_place_id()
    sdb.write(args.output_file if args.output_file is not None else args.input_file)
