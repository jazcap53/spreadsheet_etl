#!/usr/bin/python3


# file: src/extract/run_it.py
# andrew jarcho
# 2017-01-21


"""
Run the extract phase of the pipeline.

read_fns() reads raw data from the spreadsheet, and groups it by day and week.
purge_fns() removes days for which the data are incomplete.
"""

import sys
import argparse
import logging
import logging.handlers

import container_objs
import purge_fns
import read_fns
from container_objs import weeks
from tests.file_access_wrappers import FileReadAccessWrapper


def print_out(weeks):
    for week in weeks:
        container_objs.print_week(week, out=sys.stdout)
    print()


def print_buffer(buf):
    for line in buf:
        print(line)


def main():
    # from: https://docs.python.org/3/howto/logging-cookbook.html#network-logging
    rootLogger = logging.getLogger('')
    rootLogger.setLevel(logging.INFO)
    socketHandler = logging.handlers.SocketHandler('localhost',
            logging.handlers.DEFAULT_TCP_LOGGING_PORT)
    # don't bother with a formatter, since a socket handler sends the event as
    # an unformatted pickle
    rootLogger.addHandler(socketHandler)


if __name__ == '__main__':
    main()
    logging.info('extract start')
    parser = argparse.ArgumentParser()
    parser.add_argument('infile_name', help='The name of a .csv file to read')
    args = parser.parse_args()
    infile = read_fns.open_file(FileReadAccessWrapper(args.infile_name))
    # weeks = read_fns.read_lines(infile, weeks)
    # weeks = purge_fns.purge(weeks)
    # print_out(weeks)
    # buffer =
    # read_fns.read_lines(infile, weeks)
    read_fns.read_lines(infile)
    # print_buffer(buffer)
    logging.info('extract finish')
