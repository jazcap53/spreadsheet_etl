#!/usr/bin/python3

# file: src/load/load.py
# andrew jarcho
# 2017-02-20

# python: 3


import sys
import psycopg2
from spreadsheet_etl.db.config import config

# from src.extract.container_objs import Event, Day, Week

def connect():
    """
    Connect to the PostgreSQL database server
    and execute a simple query.
    """
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute('SELECT version()')
        db_version = cur.fetchone()
        print(db_version)
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def connect_2():
    """
    Connect to the PostgreSQL database server
    and execute a simple query.
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
                cur.execute('SELECT sl_insert_nap(\'{}\', \'{}\')'.format(line_list[1], line_list[2]))
                print(cur.fetchone())
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    connect_2()
