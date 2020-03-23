# file: test_chart_new.py
# andrew jarcho
# 10/2018
import os.path
import pytest
import re
from unittest.mock import Mock
from src.chart.chart_new import Chart  # , get_parse_args, ASLEEP, AWAKE, NO_DATA, QS_IN_DAY, Triple
from argparse import Namespace
from definitions import ROOT_DIR

# from tests.file_access_wrappers import FakeFileReadWrapper


def my_side_effect(q):
    if not 0 <= q < 60:
        raise ValueError
    return q


@pytest.fixture(scope="module")
def chart():
    return Chart(Namespace(debug=False,
                           infilename=os.path.join(ROOT_DIR,
                                                   'tests/',
                                                   'testdata/',
                                                   'chart_data_01.txt'),
                           outfilename=None))


def test_quarter_too_large(chart):
    with pytest.raises(ValueError):
        q = 60
        chart._get_closest_quarter = Mock(side_effect=my_side_effect(q))


def test_constants_have_good_values(chart):
    assert chart.ASLEEP == u'\u2588'  # the printed color (black ink)
    assert chart.AWAKE == u'\u0020'  # the background color (white paper)
    assert chart.NO_DATA == u'\u2591'  # gray
    assert chart.QS_IN_DAY == 96  # 24 * 4
    assert issubclass(chart.Triple, tuple)
    assert chart.infilename == os.path.join(ROOT_DIR, 'tests/',
                                            'testdata/', 'chart_data_01.txt')
    assert chart.outfilename is None


def test_get_a_line(chart):
    """Get first input line that starts with a date"""
    chart.infile = open(chart.infilename)
    chart.compile_iso_date()
    ret = chart._get_a_line()
    assert chart.curr_line == '2016-12-04'
    assert ret


def test_get_an_action_line(chart):
    """Get second input line that starts with a date"""
    chart.infile = open(chart.infilename)
    chart.compile_iso_date()
    chart._get_a_line()
    while len(chart.curr_line) == 10:  # len of an ISO date
        chart._get_a_line()
    assert chart.curr_line == 'action: Y, time: 23:45'


def test_read_file_returns_iterator(chart):
    chart.compile_iso_date()
    read_file_iterator = chart.read_file()
    assert isinstance(next(read_file_iterator), chart.Triple)


def test_advance_date(chart):
    assert chart.advance_date('2019-03-17') == '2019-03-18'


def test_advance_date_with_true_prints_ruler_before_sunday(chart, capsys):
    chart.advance_date('2019-03-16', True)  # 2019-03-16 was a Saturday
    ruler = chart.create_ruler()
    out, err = capsys.readouterr()
    assert out == ruler + '\n'
    assert err == ''


def test_advance_date_with_true_omits_ruler_before_saturday(chart, capsys):
    chart.advance_date('2019-03-15', True)
    out, err = capsys.readouterr()
    assert out == ''
    assert err == ''


def test_get_closest_quarter_with_q_60(chart):
    q = 60
    with pytest.raises(ValueError):
        chart._get_closest_quarter(q)


def test_compile_iso_date(chart):
    chart.compile_iso_date()
    assert isinstance(chart.re_iso_date, type(re.compile('Hello')))


def test_parse_input_line_raises_on_empty_input_line(chart):
    chart.curr_line = ''
    with pytest.raises(ValueError):
        chart._parse_input_line()


def test_handle_date_line_if_last_date_read_is_none(chart):
    chart.last_date_read = None
    retval = chart._handle_date_line('bongo')
    assert chart.last_start_posn == 0
    assert chart.last_date_read == 'bongo'
    assert retval == chart.Triple(-1, -1, -1)


def test_handle_date_line_if_sleep_state_is_no_data(chart):
    chart.last_date_read = '2016-12-04'
    chart.sleep_state = chart.NO_DATA
    chart.last_start_posn = 0
    assert chart._handle_date_line('bongo') == chart.Triple(0,
                                                            24 * 4,
                                                            chart.NO_DATA)


def test_handle_date_line_if_sleep_state_has_data_and_last_date_read(chart):
    chart.last_date_read = '2016-12-04'
    chart.sleep_state = chart.ASLEEP
    assert chart._handle_date_line('bongo') == chart.Triple(-1, -1, -1)


def test_handle_action_line_with_b_action(chart):
    line = 'action: b, time: 23:15, hours: 7.50'
    chart._get_start_posn = Mock(return_value=0)
    assert chart._handle_action_line(line) == chart.Triple(-1, -1, -1)


def test_handle_action_line_with_w_action(chart):
    line = 'action: w, time: 3:45, hours: 4.00'
    chart.last_sleep_time = '23:45'
    chart.last_start_posn = 95
    chart._get_num_chunks = Mock(return_value=16)
    assert chart._handle_action_line(line) == (
        chart.Triple(chart.last_start_posn, 16, chart.ASLEEP)
    )
