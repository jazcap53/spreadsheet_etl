# file: tests/test_read_fns.py
# andrew jarcho
# 2017-01-28

# pytest 3.0.7

import io
# from collections import namedtuple
import datetime
import pytest

from tests.file_access_wrappers import FakeFileReadWrapper
from src.extract.read_fns import open_infile, lines_in_weeks_out
from src.extract.read_fns import _check_for_date, _handle_start_of_night
from src.extract.read_fns import _append_week_header, _append_day_header
from src.extract.container_objs import Event, Day, Week

# TODO: at present, the 'fixture' is used in only one test
@pytest.fixture
def infile_wrapper():
    return FakeFileReadWrapper(
                u''',Sun,,,Mon,,,Tue,,,Wed,,,Thu,,,Fri,,,Sat,,
12/4/2016,,,,,,,,,,b,23:45,,w,3:45,4.00,w,2:00,2.75,b,0:00,9.00
,,,,,,,,,,,,,s,4:45,,s,3:30,,w,5:15,5.25
,,,,,,,,,,,,,w,6:15,1.50,w,8:45,5.25,s,10:30,
,,,,,,,,,,,,,s,11:30,,s,19:30,,w,11:30,1.00
,,,,,,,,,,,,,w,12:15,0.75,w,20:30,1.00,s,16:00,
,,,,,,,,,,,,,s,16:45,,,,,w,17:00,1.00
,,,,,,,,,,,,,w,17:30,0.75,,,,b,22:30,7.25
,,,,,,,,,,,,,s,21:00,,,,,,,
,,,,,,,,,,,,,w,21:30,0.50,,,,,,
,,,,,,,,,,,,,b,23:15,7.50,,,,,,
,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,
''')


def test__append_week_header():
    buffer = []
    sunday_date = datetime.date(2017, 11, 12)
    day_list = [Day(sunday_date +
                    datetime.timedelta(days=x), [])
                for x in range(7)]
    wk = Week(*day_list)
    _append_week_header(buffer, wk)
    assert buffer[-1] == '\nWeek of Sunday, 2017-11-12:\n' + '=' * 26


def test__append_day_header():
    buffer = []
    dy = Day(datetime.date(2015, 5, 5), [])
    _append_day_header(buffer, dy)
    assert buffer[-1] == '    2015-05-05'


def test__handle_start_of_night_with_3_element_b_event_outputs_and_empties_buffer():
    output = io.StringIO()
    buffer = ['bongo', 'Hello World']
    _handle_start_of_night(buffer,
                           Event(action='b', mil_time='8:15', hours='4.25'),
                           datetime.date(2017, 10, 12),
                           output)
    assert output.getvalue() == 'bongo\nHello World\n'
    assert buffer == []


def test__handle_start_of_night_with_2_element_b_event_outputs_nothing_and_pops_actions():
    output = io.StringIO()
    buffer = ['bongobongo', 'action: s, time: 19:00']
    _handle_start_of_night(buffer,
                           Event(action='b', mil_time='10:00', hours=''),
                           datetime.date(2017, 5, 17),
                           output)
    assert output.getvalue() == ''
    assert buffer == ['bongobongo']


def test__handle_start_of_night_with_2_element_b_event_and_long_b_string_in_buffer():
    output = io.StringIO()
    buffer = ['bbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', 'action: s, time: 17:00']
    _handle_start_of_night(buffer,
                           Event(action='b', mil_time='23:15', hours=''),
                           datetime.date(2017, 3, 19),
                           output)
    assert output.getvalue() == ''
    assert buffer == ['bbbbbbbbbbbbbbbbbbbbbbbbbbbbbb']


def test_open_infile(infile_wrapper):
    infile = open_infile(infile_wrapper)
    assert isinstance(infile, io.StringIO)


def test__check_for_date_matches_date_in_correct_format():
    date_string = '12/34/5678'
    good_match = _check_for_date(date_string)
    assert good_match


def test__check_for_date_rejects_date_with_hyphens():
    date_string = '12-34-5678'
    good_match = _check_for_date(date_string)
    assert not good_match


def test__check_for_date_rejects_date_with_alpha():
    date_string = 'a2/34/5678'
    good_match = _check_for_date(date_string)
    assert not good_match
