#!/usr/bin/python3

# file: src/load/load.py
# andrew jarcho
# 2017-02-20

# python: 3.5+


import sys
import psycopg2
import logging

from spreadsheet_etl.db.config import config


def decimal_to_interval(dec_str):
    """
    Convert duration from a decimal string to an interval string.
    E.g., '3.25' for 3 1/4 hours becomes '0 03:15:00'.
    """
    dec_mins_to_mins = {'00':'00', '25':'15', '50':'30', '75':'45'}
    hrs, dec_mins = dec_str.split('.')
    mins = None
    try:
        mins = dec_mins_to_mins[dec_mins]
    except KeyError:  # TODO: better way to handle bad input
        logging.error('Value for dec_mins {} not found in dec_to_mins'.format(dec_mins))
    interval_str = '0 {}:{}:00'.format(hrs, mins)
    return interval_str


def load_nights_naps(cur):
    """
    Load NIGHT and NAP data from stdin into database.
    """
    while True:
        my_line = sys.stdin.readline()
        if not my_line:
            break
        line_list = my_line.rstrip().split(', ')
        if line_list[0] == 'NIGHT':
            cur.execute('SELECT sl_insert_night(\'{}\', \'{}\')'.format(line_list[1], line_list[2]))
            logging.info(cur.fetchone())
        elif line_list[0] == 'NAP':
            duration = decimal_to_interval(line_list[2])
            cur.execute('SELECT sl_insert_nap(\'{}\', \'{}\')'.format(line_list[1], duration))
            logging.info(cur.fetchone())


def connect(store):
    """
    Connect to the PostgreSQL database server.
    Call function to load data from stdin to db.
    """
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        if store == 'True':
            load_nights_naps(cur)
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', filename='src/load/load.log', level=logging.INFO)
    connect(sys.argv[1])  # only c.l.a. will be 'True' or 'False'
