# file: tests/test_read_fns.py
# andrew jarcho
# 2017-01-28

import io
import datetime
import pytest

from tests.file_access_wrappers import FakeFileReadWrapper
from src.extract.read_fns import open_infile
from src.extract.read_fns import Extract
from container_objs import Event, Day, Week


# TODO: at present, this fixture is used in only one test
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


@pytest.fixture
def extract():
    return Extract(FakeFileReadWrapper(''))


def test_open_infile(infile_wrapper):
    infile = open_infile(infile_wrapper)
    assert isinstance(infile, io.StringIO)


def test_re_match_date_matches_date_in_correct_format(extract):
    date_string = '12/34/5678'
    date_match = extract._re_match_date(date_string)
    assert date_match


def test_re_match_date_rejects_date_with_hyphens(extract):
    date_string = '12-34-5678'
    date_match = extract._re_match_date(date_string)
    assert not date_match


def test_re_match_date_rejects_date_with_alpha(extract):
    date_string = 'a2/34/5678'
    date_match = extract._re_match_date(date_string)
    assert not date_match


def test_look_for_week_returns_false_on_non_sunday_input(extract):
    date_match = extract._re_match_date('11/14/2017')  # date is not a Sunday
    assert not extract._look_for_week(date_match)
    assert extract.sunday_date == Extract.NULL_DATE


def test_look_for_week_returns_true_on_sunday_input(extract):
    date_match = extract._re_match_date('03/31/2019')  # a Sunday
    assert extract._look_for_week(date_match)


def test_get_events_creates_events_from_non_empty_line_segments(extract):
    # shorter_line holds an 's' event for Thu and Fri, and a 'w' event for Sat
    extract.line_as_list = ['11/12/2017', '', '', '', '', '', '', '', '', '',
                            '', '', '', 's', '4:45', '', 's', '3:30', '', 'w',
                            '5:15', '5.25']
    extract.sunday_date = datetime.date(2017, 11, 12)
    day_list = [Day(extract.sunday_date +
                    datetime.timedelta(days=x), [])
                for x in range(7)]
    extract.new_week = Week(*day_list)
    have_events = extract._get_events()
    assert extract.new_week[0].events == []
    assert isinstance(extract.new_week[4].events[-1], Event)
    assert isinstance(extract.new_week[6].events[-1], Event)
    assert have_events


def test_get_events_creates_no_events_on_empty_line_input(extract):
    extract.line_as_list = ['', '', '', '', '', '', '', '', '', '', '', '',
                            '', '', '', '', '', '', '', '', '', '']
    extract.sunday_date = datetime.date(2017, 11, 5)
    day_list = [Day(extract.sunday_date +
                    datetime.timedelta(days=x), [])
                for x in range(7)]
    extract.new_week = Week(*day_list)
    have_events = extract._get_events()
    assert not have_events


def test_manage_output_buffer_leaves_last_event_in_buffer(extract):
    out_buffer = []
    extract.sunday_date = datetime.date(2017, 11, 12)
    day_list = [Day(extract.sunday_date +
                    datetime.timedelta(days=x), [])
                for x in range(7)]
    extract.new_week = Week(*day_list)
    extract.new_week[6].events.append(Event('w', '13:15', '6.5'))
    out_buffer = extract._manage_output_buffer(out_buffer)
    assert out_buffer[-1] == 'action: w, time: 13:15, hours: 6.50'


def test_manage_output_buffer_leaves_date_in_buffer_if_no_events(extract):
    out_buffer = []
    extract.sunday_date = datetime.date(2016, 4, 10)
    day_list = [Day(extract.sunday_date +
                    datetime.timedelta(days=x), [])
                for x in range(7)]
    extract.new_week = Week(*day_list)
    out_buffer = extract._manage_output_buffer(out_buffer)
    assert out_buffer[-1] == '    2016-04-16'


def test_append_week_header(extract):
    out_buffer = []
    extract.sunday_date = datetime.date(2017, 11, 12)
    day_list = [Day(extract.sunday_date +
                    datetime.timedelta(days=x), [])
                for x in range(7)]
    extract.new_week = Week(*day_list)
    out_buffer = extract._append_week_header(out_buffer)
    assert out_buffer[-1] == '\nWeek of Sunday, 2017-11-12:\n' + \
                                        '=' * 26


def test_append_day_header(extract):
    dy = Day(datetime.date(2015, 5, 5), [])
    out_buffer = extract._append_day_header(dy)
    assert out_buffer[-1] == '    2015-05-05'


def test_write_or_discard_night_3_element_b_event_flushes_buffer(extract):
    output = io.StringIO()
    out_buffer = ['bongo', 'Hello World']
    extract._write_or_discard_night(Event(action='b', mil_time='8:15',
                                          hours='4.25'),
                                    datetime.date(2017, 10, 12), out_buffer,
                                    output)
    assert output.getvalue() == 'bongo\nHello World\n'
    assert out_buffer == []


def test_write_or_discard_night_2_elem_b_event_no_output_pop_actions(extract):
    output = io.StringIO()
    out_buffer = ['bongobongo', 'action: s, time: 19:00']
    extract._write_or_discard_night(Event(action='b', mil_time='10:00',
                                          hours=''),
                                    datetime.date(2017, 5, 17), out_buffer,
                                    output)
    assert output.getvalue() == ''
    assert out_buffer == ['bongobongo']


def test_write_or_discard_night_2_elem_b_event_long_b_str_in_buffer(extract):
    output = io.StringIO()
    out_buffer = ['bbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', 'action: s, time: 17:00']
    extract._write_or_discard_night(Event(action='b', mil_time='23:15',
                                          hours=''),
                                    datetime.date(2017, 3, 19), out_buffer,
                                    output)
    assert output.getvalue() == ''
    assert out_buffer == ['bbbbbbbbbbbbbbbbbbbbbbbbbbbbbb']


def test_match_complete_b_event_line_returns_true_on_complete_b_event_line():
    line = 'action: b, time: 21:45, hours: 3.75'
    assert bool(Extract._match_complete_b_event_line(line))


def test_match_complete_b_event_line_returns_false_on_incomplete_b_event_line():
    line = 'action: b, time: 17:25'
    assert not bool(Extract._match_complete_b_event_line(line))


def test_match_complete_b_event_line_returns_false_on_non_b_event_line_input():
    line = 'action: s, time: 17:25'
    assert not bool(Extract._match_complete_b_event_line(line))


def test_match_complete_b_event_line_returns_false_on_non_event_line_input():
    line = 'cowabunga!!!'
    assert not bool(Extract._match_complete_b_event_line(line))


def test_match_event_line_returns_true_on_2_element_b_line_input():
    line = 'action: b, time: 4:25'
    assert bool(Extract._match_event_line(line))


def test_match_event_line_returns_true_on_3_element_b_line_input():
    line = 'action: b, time: 4:25, hours: 6.00'
    assert bool(Extract._match_event_line(line))


def test_match_event_line_returns_true_on_2_element_s_line_input():
    line = 'action: s, time: 4:25'
    assert bool(Extract._match_event_line(line))


def test_match_event_line_returns_true_on_3_element_w_line_input():
    line = 'action: w, time: 11:00, hours: 10.50'
    assert bool(Extract._match_event_line(line))


def test_match_event_line_returns_false_on_3_element_s_line_input():
    line = 'action: s, time: 12:00, hours: 6.00'
    assert not bool(Extract._match_event_line(line))


def test_match_event_line_returns_false_on_2_element_w_line_input():
    line = 'action: w, time: 11:45'
    assert not bool(Extract._match_event_line(line))


def test_match_event_line_returns_false_on_non_action_input():
    line = '=' * 18
    assert not bool(Extract._match_event_line(line))


# def test_handle_week_returns_true_on_