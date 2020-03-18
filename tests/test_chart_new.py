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

from tests.file_access_wrappers import FakeFileReadWrapper


def my_side_effect(q):
    if not 0 <= q < 60:
        raise ValueError
    return q


@pytest.fixture(scope="module")
def chart():
    return Chart(Namespace(debug=False,
                           filename=os.path.join(ROOT_DIR,
                                                 'tests/',
                                                 'test_chart_new.py')))


@pytest.fixture()
def chart():
    return Chart(FakeFileReadWrapper('''

Week of Sunday, 2016-12-04:
==========================
    2016-12-04
    2016-12-05
    2016-12-06
    2016-12-07
action: Y, time: 23:45
    2016-12-08
action: w, time: 3:45, hours: 4.00
action: s, time: 4:45
action: w, time: 6:15, hours: 1.50
action: s, time: 11:30
action: w, time: 12:15, hours: 0.75
action: s, time: 16:45
action: w, time: 17:30, hours: 0.75
action: s, time: 21:00
action: w, time: 21:30, hours: 0.50
action: b, time: 23:15, hours: 7.50
    2016-12-09
action: w, time: 2:00, hours: 2.75
action: s, time: 3:30
action: w, time: 8:45, hours: 5.25
action: s, time: 19:30
action: w, time: 20:30, hours: 1.00
    2016-12-10
action: b, time: 0:00, hours: 9.00
action: w, time: 5:15, hours: 5.25
action: s, time: 10:30
action: w, time: 11:30, hours: 1.00
action: s, time: 16:00
action: w, time: 17:00, hours: 1.00
action: b, time: 22:30, hours: 7.25
    '''))


@pytest.fixture()
def open_input_file(filename='/home/jazcap53/python_projects/'
                             'spreadsheet_etl/xtraneous/'
                             'transform_input_sheet_045.txt'):
    infile = open(filename)
    return infile


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


# def test_ctor_creates_instance_vars(chart):
#     assert chart.filename is not None
#     assert chart.curr_line is ''


def test_get_a_line(open_input_file, chart):
    """Get first input line that starts with a date"""
    chart.infile = open_input_file
    chart.compile_iso_date()
    ret = chart._get_a_line()
    assert chart.curr_line == '2016-12-04'
    assert ret

# def test_get_a_line_again(open_input_file, make_chart):
#     """Get second input line that starts with a date"""
#     make_chart.infile = open_input_file
#     make_chart.compile_iso_date()
#     make_chart.get_a_line()
#     make_chart.get_a_line()
#     assert make_chart.curr_line == ' 2016-12-07 | 04:45:00 | 01:30:00 |      2'


# def test_ctor_makes_a_chart(open_input_file):  # ='/home/jazcap53/python_projects/' +
#                                        # 'spreadsheet_etl/xtraneous/' +
#                                        # 'transform_input_sheet_045.txt'):
#     my_chart = Chart(open_input_file)
#     assert isinstance(my_chart, Chart)


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