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


# def test_read_file_returns_iterator(chart):
#     chart.compile_iso_date()
#     read_file_iterator = chart.read_file()
#     assert isinstance(next(read_file_iterator), chart.Triple)


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