import pytest
from src.chart.chart import Chart


@pytest.fixture()
def make_chart():
    return Chart()


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
