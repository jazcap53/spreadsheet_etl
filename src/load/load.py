# file: src/load/load.py
# andrew jarcho
# 2017-02-20

# python 2.7, 3.5


from __future__ import print_function

import psycopg2
from spreadsheet_etl.db.config import config

from src.extract.container_objs import Event, Day, Week

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

if __name__ == '__main__':
    connect()
