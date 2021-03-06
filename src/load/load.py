#!/usr/bin/env python

# file: src/load/load.py
# andrew jarcho
# 2017-02-20


import fileinput
import logging
import logging.handlers
import os
import sys

from sqlalchemy import create_engine, func


TEMP_STORE_NIGHT_CTR = 0


def decimal_to_interval(dec_str):
    """
    Convert duration from a decimal string to an interval string
    (E.g., '3.25' for 3 1/4 hours becomes '03:15').
    Called by: read_nights_naps()
    """
    dec_mins_to_mins = {'00': '00', '25': '15', '50': '30', '75': '45'}
    hrs, dec_mins = dec_str.split('.')
    try:
        mins = dec_mins_to_mins[dec_mins]
    except KeyError:
        logging.error('Value for dec_mins %d not found in '
                      'decimal_to_interval()', dec_mins)
        raise
    interval_str = '{}:{}'.format(hrs, mins)
    return interval_str


def read_nights_naps(eng, infile_name):
    """
    Read NIGHT and NAP data from infile_name;
    call function to load that data into database.

    :param eng: the db engine
    :param infile_name: read data from file or stdin
    :return: None
    Called by: connect()
    """
    global TEMP_STORE_NIGHT_CTR

    with fileinput.input(infile_name) as data_source:
        connection = eng.connect()
        trans = connection.begin()
        try:
            keep_going = True
            while keep_going:
                my_line = data_source.readline()
                keep_going = store_nights_naps(connection, my_line)
            trans.commit()
        except Exception:
            trans.rollback()
            raise


def store_nights_naps(connection, line):
    """
    Insert a line of data into the db

    If the line starts with 'NIGHT':
        insert a night into sl_night
    If the line starts with 'NAP':
        insert a nap into sl_nap

    :param connection: an open db connection
    :param line: a line of data from the transform stage
    :return: True if the line was inserted, else False
    Called by read_nights_naps()
    """
    global TEMP_STORE_NIGHT_CTR

    success = False
    line_list = line.rstrip().split(', ')
    if line_list[0] == 'NIGHT':
        TEMP_STORE_NIGHT_CTR += 1
        result = connection.execute(
            func.sl_insert_night(*line_list[1:])
        )
        for row in result:
            mesg = ', '.join(line_list)
            night_log = lambda r: ld_logger.debug(r, extra={"mesg": mesg})
            night_log(row)
        success = True
    elif line_list[0] == 'NAP':
        result = connection.execute(
            func.sl_insert_nap(line_list[1],
                               decimal_to_interval(line_list[2]),
                               TEMP_STORE_NIGHT_CTR
                               )
        )
        for row in result:
            mesg = ', '.join(line_list)
            nap_log = lambda r: ld_logger.debug(r, extra={"mesg": mesg})
            nap_log(row)
        success = True
    return success


def connect():
    """
    Connect to the PostgreSQL server

    :return: a db engine
    Called by: client code
    """
    try:
        url = os.environ['DB_URL']
    except KeyError:
        print('Please set environment variable DB_URL')
        sys.exit(1)
    else:
        eng = create_engine(url)
        return eng


def update_db(eng):
    """
    Invoke read_nights_naps() to load data from input into db.
    :param eng: the db engine
    :return: None
    """
    try:
        # if 'True' is a c.l. arg:
        #     if a file name is also a c.l. arg:
        #         read from file name
        #     else:
        #         read from stdin
        sys.argv.remove('True')
        infile_name = sys.argv[1] if len(sys.argv) > 1 else '-'
        read_nights_naps(eng, infile_name)
    except ValueError:
        pass  # don't touch the db


def main():
    """
    Set up root (network) logger and load logger
    Called by: client code
    """
    setup_network_logger()
    return setup_load_logger()


def setup_network_logger():
    """
    Set up a logger to handle messages from all processes
    :return: None
    Called by: main()
    """
    # https://docs.python.org/3/howto/logging-cookbook.html#network-logging
    root_logger = logging.getLogger('')
    root_logger.setLevel(logging.INFO)
    socket_handler = logging.handlers.SocketHandler('localhost',
                                                    logging.handlers.
                                                    DEFAULT_TCP_LOGGING_PORT)
    # don't bother with a formatter here, since a socket handler sends the
    # event as an unformatted pickle
    root_logger.addHandler(socket_handler)
    # end of logging-cookbook code


def setup_load_logger():
    """
    Setup a logger for messages from the load process only
    :return: the load logger
    Called by: main()
    """
    # ld_logger will need a formatter since it is writing to file
    load_logger = logging.getLogger('load.load')
    load_logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler('src/load/load.log', mode='w')
    formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(mesg)s')
    file_handler.setFormatter(formatter)
    load_logger.addHandler(file_handler)
    load_logger.propagate = False

    return load_logger


if __name__ == '__main__':
    ld_logger = main()
    logging.info('load start')
    engine = connect()  # only c.l.a. will be 'True' or 'False'
    update_db(engine)
    engine.dispose()
    logging.info('load finish')
