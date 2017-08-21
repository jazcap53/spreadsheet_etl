#!/usr/bin/python3

# file: src/load/load.py
# andrew jarcho
# 2017-02-20

# python: 3.5


import sys
import psycopg2
import logging
import logging.handlers
import fileinput

from db_s_etl.config import config


def decimal_to_interval(dec_str):
    """
    Convert duration from a decimal string to an interval string.
    E.g., '3.25' for 3 1/4 hours becomes '0 03:15:00'.
    """
    dec_mins_to_mins = {'00': '00', '25': '15', '50': '30', '75': '45'}
    hrs, dec_mins = dec_str.split('.')
    mins = None
    try:
        mins = dec_mins_to_mins[dec_mins]
    except KeyError:  # TODO: better way to handle bad input
        logging.error('Value for dec_mins {} not found in dec_to_mins'.
                      format(dec_mins))
    interval_str = '0 {}:{}:00'.format(hrs, mins)
    return interval_str


def load_nights_naps(cur, load_logger, infile_name):
    """
    Load NIGHT and NAP data from stdin into database.
    """
    with fileinput.input(infile_name) as data_source:
        while True:
            my_line = data_source.readline()
            if not my_line:
                break
            line_list = my_line.rstrip().split(', ')
            if line_list[0] == 'NIGHT':
                cur.execute('SELECT sl_insert_night(\'{}\', \'{}\')'.
                            format(line_list[1], line_list[2]))
                load_logger.debug(cur.fetchone())
            elif line_list[0] == 'NAP':
                duration = decimal_to_interval(line_list[2])
                cur.execute('SELECT sl_insert_nap(\'{}\', \'{}\')'.
                            format(line_list[1], duration))
                load_logger.debug(cur.fetchone())


def connect(load_logger):
    """
    Connect to the PostgreSQL database server.
    Call function to load data from stdin to db_s_etl.
    """
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        try:
            # if 'True' is a c.l. arg:
            #     if a file name is also a c.l. arg:
            #         read from file name
            #     else:
            #         read from stdin
            sys.argv.remove('True')
            infile_name = sys.argv[1] if len(sys.argv) > 1 else '-'
            load_nights_naps(cur, load_logger, infile_name)
        except ValueError:
            pass  # don't touch the db
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        if conn is not None:
            conn.close()


def main():
    # https://docs.python.org/3/howto/logging-cookbook.html#network-logging
    rootLogger = logging.getLogger('')
    rootLogger.setLevel(logging.INFO)
    socketHandler = logging.handlers.SocketHandler('localhost',
            logging.handlers.DEFAULT_TCP_LOGGING_PORT)
    # don't bother with a formatter here, since a socket handler sends the
    # event as an unformatted pickle
    rootLogger.addHandler(socketHandler)
    # end of logging-cookbook code

    # load_logger will need a formatter since it is writing to file
    load_logger = logging.getLogger('load.load')
    load_logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler('src/load/load.log', mode='w')
    formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    load_logger.addHandler(file_handler)
    load_logger.propagate = False

    return load_logger


if __name__ == '__main__':
    load_logger = main()
    logging.info('load start')
    connect(load_logger)  # only c.l.a. will be 'True' or 'False'
    logging.info('load finish')
