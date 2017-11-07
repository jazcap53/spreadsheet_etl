#!/usr/bin/python3


# file: src/extract/run_it.py
# andrew jarcho
# 2017-01-21


"""
Run the extract phase of the pipeline.

read_fns() reads raw data from the spreadsheet, and groups it by day and week.
"""

# import sys
import argparse
import logging
import logging.handlers

# import container_objs
import read_fns
from tests.file_access_wrappers import FileReadAccessWrapper


def main():
    # from: https://docs.python.org/3/howto/logging-cookbook.html#network-logging
    rootLogger = logging.getLogger('')
    rootLogger.setLevel(logging.INFO)
    socketHandler = logging.handlers.SocketHandler('localhost',
            logging.handlers.DEFAULT_TCP_LOGGING_PORT)
    # don't bother with a formatter, since a socket handler sends the event as
    # an unformatted pickle
    rootLogger.addHandler(socketHandler)

    # read_logger will need a formatter since it is writing to file
    read_logger = logging.getLogger('extract.read_fns')
    read_logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler('src/extract/read_fns.log', mode='w')
    formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    read_logger.addHandler(file_handler)
    read_logger.propagate = False


if __name__ == '__main__':
    main()
    logging.info('extract start')
    parser = argparse.ArgumentParser()
    parser.add_argument('infile_name', help='The name of a .csv file to read')
    args = parser.parse_args()
    infile = read_fns.open_file(FileReadAccessWrapper(args.infile_name))
    read_fns.lines_in_weeks_out(infile)
    logging.info('extract finish')
