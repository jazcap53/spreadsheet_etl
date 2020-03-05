# file: test_chart_new.py
# andrew jarcho
# 10/2018
import pytest
from unittest.mock import Mock
from src.chart.chart_new import Chart  # , get_parse_args, ASLEEP, AWAKE, NO_DATA, QS_IN_DAY, Triple
from argparse import Namespace


def my_side_effect(q):
    if not 0 <= q < 60:
        raise ValueError
    return q


@pytest.fixture(scope="module")
def chart():
    return Chart(Namespace(debug=False,
                           filename='/home/jazcap53/python_projects'
                                    '/spreadsheet_etl/tests'
                                    '/test_chart_new.py'))


def test_quarter_too_large(chart):
    with pytest.raises(ValueError):
        q = 60
        chart._get_closest_quarter = Mock(side_effect=my_side_effect(q))



# from collections import namedtuple
# from tests.file_access_wrappers import FakeFileReadWrapper
# import _io


# @pytest.fixture()
# def chart():
#     return Chart(FakeFileReadWrapper('''
#  sleep_date | nap_time | duration | nap_id
# ------------+----------+----------+--------
#  2016-12-07 | 23:45:00 | 04:00:00 |      1
#  2016-12-07 | 04:45:00 | 01:30:00 |      2
#  2016-12-07 | 11:30:00 | 00:45:00 |      3
#  2016-12-07 | 16:45:00 | 00:45:00 |      4
#  2016-12-07 | 21:00:00 | 00:30:00 |      5
#  2016-12-08 | 23:15:00 | 02:45:00 |      6
#  2016-12-08 | 03:30:00 | 05:15:00 |      7
#  2016-12-08 | 19:30:00 | 01:00:00 |      8
#  2016-12-09 |          |          |
#  2016-12-10 | 00:00:00 | 05:15:00 |      9
#  2016-12-10 | 10:30:00 | 01:00:00 |     10
#  2016-12-10 | 16:00:00 | 01:00:00 |     11
#  2016-12-10 | 22:30:00 | 01:45:00 |     12
#  2016-12-10 | 02:30:00 | 02:45:00 |     13
#  2016-12-10 | 11:00:00 | 01:00:00 |     14
#  2016-12-10 | 17:15:00 | 00:45:00 |     15
#  2016-12-10 | 19:15:00 | 01:00:00 |     16
#     '''))


# @pytest.fixture()
# def open_input_file(filename='/home/jazcap53/python_projects/' +
#                              'spreadsheet_etl/src/chart/chart_raw_data.txt'):
#     infile = open(filename)
#     return infile


# def test_constants_have_good_values(chart):
#
#     assert chart.ASLEEP == u'\u2588'  # the printed color (black ink)
#     assert chart.AWAKE == u'\u0020'  # the background color (white paper)
#     assert chart.NO_DATA == u'\u2591'
#     assert chart.QS_IN_DAY == 96  # 24 * 4
#     assert issubclass(chart.Triple, tuple)
#
#
# def test_ctor_creates_instance_vars(chart):
#     assert chart.filename is not None
#     assert chart.curr_line is ''


# def test_get_a_line(open_input_file, make_chart):
#     """Get first input line that starts with a date"""
#     make_chart.infile = open_input_file
#     make_chart.compile_iso_date()
#     make_chart.get_a_line()
#     assert make_chart.curr_line == ' 2016-12-07 | 23:45:00 | 04:00:00 |      1'


# def test_get_a_line_again(open_input_file, make_chart):
#     """Get second input line that starts with a date"""
#     make_chart.infile = open_input_file
#     make_chart.compile_iso_date()
#     make_chart.get_a_line()
#     make_chart.get_a_line()
#     assert make_chart.curr_line == ' 2016-12-07 | 04:45:00 | 01:30:00 |      2'


# def test_ctor_makes_a_chart(input_file='/home/jazcap53/python_projects/' +
#                                        'spreadsheet_etl/src/chart/' +
#                                        'chart_raw_data.txt'):
#     my_chart = Chart(input_file)
#     assert isinstance(my_chart, Chart)


# def test_read_file_returns_iterator(input_file='/home/jazcap53/' +
#                                                'python_projects/' +
#                                                'spreadsheet_etl/src/chart/' +
#                                                'chart_raw_data.txt'):
#     my_chart = Chart(input_file)
#     my_chart.compile_iso_date()
#     read_file_iterator = my_chart.read_file()
#     assert isinstance(next(read_file_iterator), Triple)


# def test_advance_date(chart):
#     assert chart.advance_date('2019-03-17') == '2019-03-18'
#
#
# def test_advance_date_with_true_prints_ruler_before_sunday(chart, capsys):
#     chart.advance_date('2019-03-16', True)
#     ruler = chart.create_ruler()
#     out, err = capsys.readouterr()
#     assert out == ruler + '\n'
#     assert err == ''
#
#
# def test_advance_date_with_true_omits_ruler_before_saturday(chart, capsys):
#     chart.advance_date('2019-03-15', True)
#     out, err = capsys.readouterr()
#     assert out == ''
#     assert err == ''

# def test_get_closest_quarter_with_q_60(chart):
#     q = 60
#     with pytest.raises(ValueError):
#         chart._get_closest_quarter(q)
