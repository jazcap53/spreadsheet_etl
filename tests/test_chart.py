import pytest
from src.chart.chart import Chart


@pytest.fixture()
def make_chart():
    return Chart()


def test_get_half_hr_if_0(make_chart):
    assert make_chart.get_half_hr(0) == '\u0020'


def test_get_half_hr_if_1(make_chart):
    assert make_chart.get_half_hr(1) == '\u2590'


def test_get_half_hr_if_2(make_chart):
    assert make_chart.get_half_hr(2) == '\u258c'


def test_get_half_hr_if_3(make_chart):
    assert make_chart.get_half_hr(3) == '\u2588'


def test_get_half_hr_if_7(make_chart):
    assert make_chart.get_half_hr(7) == '\u2591'


def test_make_out_string_with_valid_input(make_chart):
    line_in = bytearray('771333200013332000133320001333200013332000133320', 'utf-8')
    assert len(line_in) == 48
    temp2 = make_chart.make_out_string(line_in)
    line_out = '|' + temp2 + '|\n'
    assert len(line_out) == 51
    assert line_out == '|░░▐███▌   ▐███▌   ▐███▌   ▐███▌   ▐███▌   ▐███▌ |\n'

