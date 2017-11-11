import pytest
from datetime import datetime
import os
import sys
from sqlalchemy import create_engine, text


@pytest.fixture(scope="module")
def my_setup():
    try:
        url = 'postgresql://{}:{}@localhost/sleep_test'.format(
                os.environ['DB_TEST_USERNAME'], os.environ['DB_TEST_PASSWORD'])
    except KeyError:
        print('Please set the environment variables DB_TEST_USERNAME and '
              'DB_TEST_PASSWORD')
        sys.exit(1)
    engine = create_engine(url)
    return engine


def test_inserting_a_night_adds_one_to_night_count(my_setup):
    date_time_now = datetime.now()
    date_today = date_time_now.date().isoformat()
    time_now = date_time_now.time().isoformat()
    last_colon_at = time_now.rfind(':')
    time_now = time_now[:last_colon_at] + ':00'
    engine = my_setup
    connection = engine.connect()
    result = connection.execute("select count (*) from slt_night")
    orig_ct = result.fetchone()[0]
    sql = text("INSERT INTO slt_night (start_date, start_time)"
               " values (:date_today, :time_now)")
    data = {'date_today': date_today, 'time_now': time_now}
    connection.execute(sql, data)
    result = connection.execute("select count (*) from slt_night")
    new_ct = result.fetchone()[0]
    assert orig_ct + 1 == new_ct
