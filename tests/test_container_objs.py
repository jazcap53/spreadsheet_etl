# file: test/test_container_objs.py
# andrew jarcho
# 2016-01-08

# pytest: 3.0.7


from datetime import date, timedelta
import pytest
import io

from src.extract.container_objs import validate_segment, Event, Day, Week
from src.extract.container_objs import print_event


# test validate_segment()

def test_empty_segment_returns_false(seg=['', '', '']):
    assert not validate_segment(seg)


def test_non_null_segment_and_not_item_0_returns_false(seg=['', '4:15', '']):
    assert not validate_segment(seg)


def test_first_char_of_item_0_is_not_valid_returns_false(seg=['x', '11:30', '2.50']):
    assert not validate_segment(seg)


def test_extra_space_in_item_0_returns_true(seg=['b ', '22:45', '7.50']):
    assert validate_segment(seg)


def test_item_0_is_s_and_item_2_is_not_blank_returns_false(seg=['s', '10:00', '1.00']):
    assert not validate_segment(seg)


def test_item_0_is_w_and_item_2_is_blank_returns_false(seg=['w', '0:00', '']):
    assert not validate_segment(seg)


def test_item_2_is_not_blank_and_does_not_match_regex_returns_false(seg=['w', '1:00', '1.a5']):
    assert not validate_segment(seg)


# test Event class

def test_Event_ctor_raises_TypeError_if_segment_len_gt_3():
    segment = ['w', '12:45', '3.75', 'bongo']
    with pytest.raises(TypeError):
        my_event = Event(*segment)


def test_Event_ctor_raises_TypeError_if_segment_len_lt_3():
    segment = ['s', '23:30']
    with pytest.raises(TypeError):
        my_event = Event(*segment)


def test_Event_ctor_creates_valid_Event_with_valid_input_segment():
    segment = ['b', '0:00', '7.50']
    my_event = Event(*segment)
    assert my_event.action == 'b'
    assert my_event.mil_time == '0:00'
    assert my_event.hours == '7.50'


def test_Event_ctor_creates_valid_Event_with_valid_hours_empty_input_segment():
    segment = ['s', '13:15', '']
    my_event = Event(*segment)
    assert my_event.action == 's'
    assert my_event.mil_time == '13:15'
    assert my_event.hours == ''


def test_print_event_outputs_valid_string_on_valid_input_segment():
    segment = ['b', '0:45', '6.30']
    my_event = Event(*segment)
    my_output = io.StringIO()
    print_event(my_event, my_output)
    my_string = my_output.getvalue()
    assert my_string == u'action: b, time: 0:45, hours: 6.30\n'


def test_print_event_outputs_valid_string_on_valid_short_input_segment():
    segment = ['s', '11:15', '']
    my_event = Event(*segment)
    my_output = io.StringIO()
    print_event(my_event, my_output)
    my_string = my_output.getvalue()
    assert my_string == u'action: s, time: 11:15\n'


# test Day class

@pytest.fixture
def make_day():
    return Day(date(2017, 1, 9), [])


def test_Day_has_a_datetime_dt_date_member(make_day):
    assert isinstance(make_day.dt_date, date)


def test_Day_member_events_starts_as_an_empty_list(make_day):
    assert isinstance(make_day.events, list)
    assert len(make_day.events)== 0


def test_appending_event_to_Day_dot_events_is_successful(make_day):
    make_day.events.append(Event('s', '23:45', ''))
    assert len(make_day.events) == 1

# note: creating a bad event should now cause a write to read_fns.log
# def test_creating_a_bad_event_raises_ValueError(make_day):
#     with pytest.raises(ValueError):
#         make_day.events.append(Event('x', '4:00', '1.75'))


# test Week class

@pytest.fixture
def make_week():
    dts = [Day(date(2017, 1, 15) + timedelta(days=x), [])
            for x in range(7)]
    return Week(*dts)


def test_initializing_Week_with_non_Sunday_date_raises_ValueError(make_week):
    dts = [Day(date(2017, 1, 14) + timedelta(days=x), [])
            for x in range(7)]
    with pytest.raises(ValueError):
        my_other_week = Week(*dts)


def test_first_day_of_Week_is_Sunday(make_week):
    assert make_week[0].dt_date.weekday() == 6


def test_a_Week_has_seven_Days(make_week):
    assert len(make_week) == 7


def test_days_two_thru_seven_of_Week_have_no_Sunday(make_week):
    # f checks that day x is a Sunday
    f = lambda x: make_week[x].dt_date.weekday() == 6
    assert not any(f(x) for x in range(1, 7))
