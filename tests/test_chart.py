# file: test_chart.py
# andrew jarcho
# 10/2018


import pytest
from src.chart.chart import Chart
from tests.file_access_wrappers import FakeFileReadWrapper
import _io


'''
Note:
    ASLEEP = 0b0  # the printed color (black ink)
    AWAKE = 0b1  # the background color (white paper)
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
    assert make_chart.to_glyph == {0: '\u2588', 1: '\u258c', 2: '\u2590',
                                   3: '\u0020', 7: '\u2591'}
    assert make_chart.ASLEEP == 0b0
    assert make_chart.AWAKE == 0b1


def test_ctor_creates_instance_vars(make_chart):
    assert make_chart.filename is not None
    assert make_chart.cur_line is ''


def test_quarter_to_wake_digit(make_chart):
    q = True
    quarter = make_chart.quarter_to_digit(q)
    assert quarter == make_chart.AWAKE


def test_quarter_to_sleep_digit(make_chart):
    q = False
    quarter = make_chart.quarter_to_digit(q)
    assert quarter == make_chart.ASLEEP


def test_quarters_to_glyph_code_00(make_chart):
    hi = make_chart.ASLEEP
    lo = make_chart.ASLEEP
    code = make_chart.quarters_to_glyph_code(hi, lo)
    assert code == 0


def test_quarters_to_glyph_code_01(make_chart):
    hi = make_chart.ASLEEP
    lo = make_chart.AWAKE
    code = make_chart.quarters_to_glyph_code(hi, lo)
    assert code == 1


def test_quarters_to_glyph_code_10(make_chart):
    hi = make_chart.AWAKE
    lo = make_chart.ASLEEP
    code = make_chart.quarters_to_glyph_code(hi, lo)
    assert code == 2


def test_quarters_to_glyph_code_11(make_chart):
    hi = make_chart.AWAKE
    lo = make_chart.AWAKE
    code = make_chart.quarters_to_glyph_code(hi, lo)
    assert code == 3


def test_make_glyph_if_0(make_chart):
    assert make_chart.make_glyph(0) == '\u2588'


def test_make_glyph_if_1(make_chart):
    assert make_chart.make_glyph(1) == '\u258c'


def test_make_glyph_if_2(make_chart):
    assert make_chart.make_glyph(2) == '\u2590'


def test_make_glyph_if_3(make_chart):
    assert make_chart.make_glyph(3) == '\u0020'


def test_make_glyph_if_7(make_chart):
    assert make_chart.make_glyph(7) == '\u2591'


def test_make_out_string_with_valid_input(make_chart):
    line_in = bytearray('771333200013332000133320001333200013332000133320',
                        'utf-8')
    assert len(line_in) == 48
    temp2 = make_chart.make_out_string(line_in)
    line_out = '|' + temp2 + '|\n'
    assert len(line_out) == 51
    assert line_out == '|░░▌   ▐███▌   ▐███▌   ▐███▌   ▐███▌   ▐███▌   ▐█|\n'


def test_make_out_string_with_invalid_digit(make_chart):
    with pytest.raises(KeyError):
        # '8' in line_in
        line_in = bytearray(
            '771333200013332000133320801333200013332000133320', 'utf-8')
        make_chart.make_out_string(line_in)


def test_make_out_string_with_empty_string(make_chart):
    with pytest.raises(AssertionError):
        line_in = bytearray('', 'utf-8')
        make_chart.make_out_string(line_in)


def test_get_a_line(open_input_file, make_chart):
    """Get first input line that starts with a date"""
    make_chart.infile = open_input_file
    make_chart.compile_date_checker()
    make_chart.get_a_line()
    assert make_chart.cur_line == ' 2016-12-07 | 23:45:00 | 04:00:00 |      1'


def test_get_a_line_again(open_input_file, make_chart):
    """Get second input line that starts with a date"""
    make_chart.infile = open_input_file
    make_chart.compile_date_checker()
    make_chart.get_a_line()
    make_chart.get_a_line()
    assert make_chart.cur_line == ' 2016-12-07 | 04:45:00 | 01:30:00 |      2'


@pytest.mark.run_occasionally
def test_open_file(input_file='/home/jazcap53/python_projects/' +
                              'spreadsheet_etl/src/chart/chart_raw_data.txt'):
    my_chart = Chart(input_file)
    my_chart.compile_date_checker()
    my_chart.open_file()
    assert isinstance(my_chart.infile, _io.TextIOWrapper)
    my_chart.infile.close()
