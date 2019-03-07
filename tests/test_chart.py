# file: test_chart.py
# andrew jarcho
# 10/2018


import pytest
from src.chart.chart import Chart
from tests.file_access_wrappers import FakeFileReadWrapper
import _io


'''
Note:
    ASLEEP == 1  # the printed color (black ink)
    AWAKE == 0   # the background color (white paper)
'''


@pytest.fixture()
def make_chart():
    return Chart(FakeFileReadWrapper('''
 sleep_date | nap_time | duration | nap_id 
------------+----------+----------+--------
 2016-12-07 | 23:45:00 | 04:00:00 |      1
 2016-12-07 | 04:45:00 | 01:30:00 |      2
 2016-12-07 | 11:30:00 | 00:45:00 |      3
 2016-12-07 | 16:45:00 | 00:45:00 |      4
 2016-12-07 | 21:00:00 | 00:30:00 |      5
 2016-12-08 | 23:15:00 | 02:45:00 |      6
 2016-12-08 | 03:30:00 | 05:15:00 |      7
 2016-12-08 | 19:30:00 | 01:00:00 |      8
 2016-12-09 |          |          |       
 2016-12-10 | 00:00:00 | 05:15:00 |      9
 2016-12-10 | 10:30:00 | 01:00:00 |     10
 2016-12-10 | 16:00:00 | 01:00:00 |     11
 2016-12-10 | 22:30:00 | 01:45:00 |     12
 2016-12-10 | 02:30:00 | 02:45:00 |     13
 2016-12-10 | 11:00:00 | 01:00:00 |     14
 2016-12-10 | 17:15:00 | 00:45:00 |     15
 2016-12-10 | 19:15:00 | 01:00:00 |     16    
    '''))


@pytest.fixture()
def open_input_file(filename='/home/jazcap53/python_projects/' +
                             'spreadsheet_etl/src/chart/chart_raw_data.txt'):
    infile = open(filename)
    return infile


def test_ctor_creates_class_vars(make_chart):
    assert make_chart.ASLEEP == 1
    assert make_chart.AWAKE == 0


def test_ctor_creates_instance_vars(make_chart):
    assert make_chart.filename is not None
    assert make_chart.cur_line is ''


def test_get_a_line(open_input_file, make_chart):
    """Get first input line that starts with a date"""
    make_chart.infile = open_input_file
    make_chart.compile_date_re()
    make_chart.get_a_line()
    assert make_chart.cur_line == ' 2016-12-07 | 23:45:00 | 04:00:00 |      1'


def test_get_a_line_again(open_input_file, make_chart):
    """Get second input line that starts with a date"""
    make_chart.infile = open_input_file
    make_chart.compile_date_re()
    make_chart.get_a_line()
    make_chart.get_a_line()
    assert make_chart.cur_line == ' 2016-12-07 | 04:45:00 | 01:30:00 |      2'


@pytest.mark.run_occasionally
def test_open_file(input_file='/home/jazcap53/python_projects/' +
                              'spreadsheet_etl/src/chart/chart_raw_data.txt'):
    my_chart = Chart(input_file)
    my_chart.compile_date_re()
    my_chart.open_file()
    assert isinstance(my_chart.infile, _io.TextIOWrapper)
    my_chart.infile.close()
