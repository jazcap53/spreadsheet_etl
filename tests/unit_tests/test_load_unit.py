import pytest
from src.load.load import decimal_to_interval, setup_load_logger, main


def test_decimal_to_interval():
    good_input = '3.25'
    assert decimal_to_interval(good_input) == '3:15'


def test_decimal_to_interval_with_bad_decimal_raises():
    bad_input = '3.14'
    with pytest.raises(KeyError):
        decimal_to_interval(bad_input)


def test_setup_load_logger():
    lgr = setup_load_logger()
    assert lgr
    assert lgr.propagate == False


def test_main():
    assert main()
