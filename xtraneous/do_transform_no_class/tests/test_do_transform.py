# file: tests/test_do_transform.py
# andrew jarcho
# 2017-03-15

# pytest 3.0.7


import pytest
import sys
from contextlib import contextmanager
from io import StringIO

from spreadsheet_etl.xtraneous.do_transform_no_class.do_transform import process_curr


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


def test_call_to_inner_with_date_line_stores_last_date(inner):
    cur_l = '    2017-01-12'
    inner(cur_l)
    assert len(inner.__code__.co_freevars) == 6
    assert inner.__code__.co_freevars[2] == 'last_date'
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


def test_call_to_inner_with_date_and_action_s_action_w_outputs_NAP(inner):
    cur_l = '    2016-09-12'
    inner(cur_l)
    cur_l = 'action: s, time: 03:00'
    inner(cur_l)
    cur_l = 'action: w, time: 04:15, hours: 01.15'
    with captured_output() as (out, err):
        inner(cur_l)
    output = out.getvalue().strip()
    assert output == 'NAP, 04:15, 01.25'
