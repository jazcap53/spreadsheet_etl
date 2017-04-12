#!/usr/bin/python3

# file: src/load/load.py
# andrew jarcho
# 2017-02-20

# python: 3


import sys
import psycopg2
from spreadsheet_etl.db.config import config


def decimal_to_interval(dec_str):
    dec_mins_to_mins = {'00':'00', '25':'15', '50':'30', '75':'45'}
    hrs, dec_mins = dec_str.split('.')
    try:
        mins = dec_mins_to_mins[dec_mins]
    except KeyError:  # TODO: better way to handle bad input
        print('Value for dec {} not found in dec_to_mins'.format(dec))
    interval_str = '0 {}:{}:00'.format(hrs, mins)
    return interval_str


def connect_and_load():  # TODO: separate into two functions?
    """
    Connect to the PostgreSQL database server
    and load data from stdin.
    """
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        last_serial_val = 0
        while True:
            my_line = sys.stdin.readline()
            if not my_line:
                break
            line_list = my_line.rstrip().split(', ')
            if line_list[0] == 'NIGHT':
                cur.execute('SELECT sl_insert_night(\'{}\', \'{}\')'.format(line_list[1], line_list[2]))
                print(cur.fetchone())
            elif line_list[0] == 'NAP':
                duration = decimal_to_interval(line_list[2])
                cur.execute('SELECT sl_insert_nap(\'{}\', \'{}\')'.format(line_list[1], duration))
                print(cur.fetchone())
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    connect_and_load()
