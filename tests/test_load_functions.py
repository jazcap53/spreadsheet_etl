import pytest
from sqlalchemy import create_engine, select, func, table


@pytest.fixture(scope="module")
def my_setup():
    url = 'postgresql://jazcap53:test@localhost/sleep'
    engine = create_engine(url)
    return engine


def test_inserting_a_night_adds_one_to_night_count(my_setup):
    engine = my_setup
    connection = engine.connect()
    # result = connection.execute("select([func.count()]).select_from(table)")
    result = connection.execute("select count (*) from sl_night")
    orig_ct = result.fetchone()[0]
    connection.execute("insert into sl_night (start_date, start_time)"
                       " values('2017-08-05', '07:15')")
    result = connection.execute("select count (*) from sl_night")
    new_ct = result.fetchone()[0]
    assert orig_ct + 1 == new_ct
    # print('orig_ct is {}'.format(orig_ct))

