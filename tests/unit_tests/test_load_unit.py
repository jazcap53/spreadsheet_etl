from src.load.load import decimal_to_interval


def test_good_interval_returns_good_output_on_good_input():
    good_input = '3.25'
    assert decimal_to_interval(good_input) == '3:15'
