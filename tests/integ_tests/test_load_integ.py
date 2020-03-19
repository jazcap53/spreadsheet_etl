import pytest
import os
import sys
from datetime import datetime

from sqlalchemy import text

from src.load.load import create_engine


@pytest.yield_fixture(scope="module")
def connection():
    try:
        url = os.environ['DB_URL_TEST']
    except KeyError:
        print('Please set environment variable DB_URL_TEST')
        sys.exit(1)
    eng = create_engine(url)
    conn = eng.connect()
    conn.execute('ALTER SEQUENCE slt_night_night_id_seq RESTART WITH 1')
    conn.execute('ALTER SEQUENCE slt_nap_nap_id_seq RESTART WITH 1')
    yield conn
    conn.execute('DELETE FROM slt_nap')
    conn.execute('DELETE FROM slt_night')
    eng.dispose()


def test_inserting_a_night_adds_one_to_night_count(connection):
    date_time_now = datetime.now()
    date_today = date_time_now.date().isoformat()
    time_now = date_time_now.time().isoformat()
    last_colon_at = time_now.rfind(':')
    time_now = time_now[:last_colon_at] + ':00'
    result = connection.execute("SELECT count(night_id) FROM slt_night")
    orig_ct = result.fetchone()[0]
    sql = text("INSERT INTO slt_night (start_date, start_time) "
               "VALUES (:date_today, :time_now)")
    data = {'date_today': date_today, 'time_now': time_now}
    connection.execute(sql, data)
    result = connection.execute("SELECT count(night_id) FROM slt_night")
    new_ct = result.fetchone()[0]
    assert orig_ct + 1 == new_ct


def test_inserting_a_nap_adds_one_to_nap_count(connection):
    start_time_now = datetime.now().time()
    duration = '02:45'
    night_id_result = connection.execute("SELECT max(night_id) FROM slt_night")
    night_id = night_id_result.fetchone()[0]
    result = connection.execute("SELECT count(nap_id) FROM slt_nap")
    orig_ct = result.fetchone()[0]
    sql = text("INSERT INTO slt_nap(start_time, duration, night_id) "
               "VALUES (:start_time_now, :duration, :night_id_result)")
    data = {'start_time_now': start_time_now, 'duration': duration,
            'night_id_result': night_id}
    connection.execute(sql, data)
    result = connection.execute("SELECT count(nap_id) FROM slt_nap")
    new_ct = result.fetchone()[0]
    assert orig_ct + 1 == new_ct
