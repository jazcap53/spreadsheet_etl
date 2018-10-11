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


def test_get_half_hr_if_neg_1(make_chart):
    assert make_chart.get_half_hr(-1) == '\u2591'

