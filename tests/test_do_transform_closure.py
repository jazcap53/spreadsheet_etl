# file: tests/test_do_transform_closure.py
# andrew jarcho
# 2017-03-15

# pytest 3.0.7


import pytest
import sys
from contextlib import contextmanager
from io import StringIO

from spreadsheet_etl.src.transform.do_transform_closure import process_curr


# Note: inner.__code__.co_freevars is a tuple holding the values of inner's
#       free variables in alpha order. Currently this is (get_duration,
#       get_wake_or_last_sleep, last_date, last_sleep_time, multiplier,
#       out_val).


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


@pytest.fixture
def inner():
    return process_curr()


def test_co_freevars_holds_value_we_think_it_does(inner):
    assert inner.__code__.co_freevars == ('get_duration',
            'get_wake_or_last_sleep', 'last_date', 'last_sleep_time',
            'multiplier', 'out_val')


def test_empty_line_input_has_no_effect(inner):
    cur_l = ''
    inner(cur_l)
    assert inner.__closure__[5].cell_contents is None  # out_val
    assert inner.__closure__[2].cell_contents == ''    # last_date
    assert inner.__closure__[3].cell_contents == ''    # last_sleep_time
    assert inner.__closure__[4].cell_contents == 0     # multiplier


def test_Week_of_input_has_no_effect(inner):
    cur_l = 'Week of Sunday, 2017-03-19:'
    inner(cur_l)
    assert inner.__closure__[5].cell_contents is None  # out_val
    assert inner.__closure__[2].cell_contents == ''    # last_date
    assert inner.__closure__[3].cell_contents == ''    # last_sleep_time
    assert inner.__closure__[4].cell_contents == 0     # multiplier


def test_line_of_equals_signs_has_no_effect(inner):
    cur_l = '==========================='
    inner(cur_l)
    assert inner.__closure__[5].cell_contents is None  # out_val
    assert inner.__closure__[2].cell_contents == ''    # last_date
    assert inner.__closure__[3].cell_contents == ''    # last_sleep_time
    assert inner.__closure__[4].cell_contents == 0     # multiplier


def test_call_to_inner_with_date_stores_last_date(inner):
    cur_l = '    2017-01-12'
    inner(cur_l)
    assert inner.__closure__[2].cell_contents == '2017-01-12'


def test_call_to_inner_with_action_b_stores_last_sleep_time(inner):
    cur_l = 'action: b, time: 0:00, hours: 9.00'
    inner(cur_l)
    assert inner.__closure__[3].cell_contents == '00:00'  # __closure__[3] is last_sleep_time


def test_call_to_inner_with_date_and_action_b_outputs_NIGHT(inner):
    cur_l = '    2017-01-12'
    inner(cur_l)
    cur_l = 'action: b, time: 0:00, hours: 9.00'
    with captured_output() as (out, err):
        inner(cur_l)
    output = out.getvalue().strip()
    assert output == 'NIGHT, 2017-01-12, 00:00'


def test_call_to_inner_with_action_s_stores_last_sleep_time(inner):
    cur_l = 'action: s, time: 13:15'
    inner(cur_l)
    assert inner.__closure__[3].cell_contents == '13:15'


def test_call_to_inner_with_date_and_action_s_and_action_w_outputs_NAP(inner):
    cur_l = '    2016-09-12'
    inner(cur_l)
    cur_l = 'action: s, time: 03:00'
    inner(cur_l)
    cur_l = 'action: w, time: 04:15, hours: 01.15'
    with captured_output() as (out, err):
        inner(cur_l)
    output = out.getvalue().strip()
    assert output == 'NAP, 04:15, 01.25'
