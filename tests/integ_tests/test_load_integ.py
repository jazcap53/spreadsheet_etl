from datetime import datetime
from sqlalchemy import text
import textwrap


def test_inserting_a_night_adds_one_to_night_count(cnxn):
    date_time_now = datetime.now()
    date_today = date_time_now.date().isoformat()
    time_now = date_time_now.time().isoformat()
    last_colon_at = time_now.rfind(':')
    time_now = time_now[:last_colon_at] + ':00'

    stmnt = textwrap.dedent('''
    SELECT count(night_id) FROM slt_night
    ''')
    result = cnxn.execute(stmnt)
    orig_ct = result.fetchone()[0]

    stmnt = text(textwrap.dedent('''
    INSERT INTO slt_night (start_date, start_time) 
    VALUES (:date_today, :time_now)
    '''))
    data = {'date_today': date_today, 'time_now': time_now}
    cnxn.execute(stmnt, data)

    stmnt = textwrap.dedent('''
    SELECT count(night_id) FROM slt_night
    ''')
    result = cnxn.execute(stmnt)
    new_ct = result.fetchone()[0]
    assert orig_ct + 1 == new_ct


def test_inserting_a_nap_adds_one_to_nap_count(cnxn):
    start_time_now = datetime.now().time()
    duration = '02:45'
    stmnt = textwrap.dedent('''
    SELECT max(night_id) FROM slt_night
    ''')
    night_id_result = cnxn.execute(stmnt)
    night_id = night_id_result.fetchone()[0]

    stmnt = textwrap.dedent('''
    SELECT count(nap_id) FROM slt_nap
    ''')
    result = cnxn.execute(stmnt)
    orig_ct = result.fetchone()[0]

    stmnt = text(textwrap.dedent('''
    INSERT INTO slt_nap(start_time, duration, night_id) 
    VALUES (:start_time_now, :duration, :night_id_result)
    '''))
    data = {'start_time_now': start_time_now, 'duration': duration,
            'night_id_result': night_id}
    cnxn.execute(stmnt, data)

    stmnt = textwrap.dedent('''
    SELECT count(nap_id) FROM slt_nap
    ''')
    result = cnxn.execute(stmnt)
    new_ct = result.fetchone()[0]
    assert orig_ct + 1 == new_ct
