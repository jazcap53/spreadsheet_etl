# file: tests/test_do_transform.py
# andrew jarcho
# 2017-03-15

# pytest 3.0.7


import pytest

from tests.file_access_wrappers import FakeFileReadWrapper
from src.transform.do_transform import Transform


def test_read_blank_line_does_not_change_state():
    file_wrapper = FakeFileReadWrapper('\n')
    my_transform = Transform(file_wrapper)
    my_transform.read_each_line()
    assert my_transform.last_date == ''
    assert my_transform.last_sleep_time == ''


def test_read_week_of_line_does_not_change_state():
    file_wrapper = FakeFileReadWrapper('Week of Sunday, 2016-12-04:\n')
    my_transform = Transform(file_wrapper)
    my_transform.read_each_line()
    assert my_transform.last_date == ''
    assert my_transform.last_sleep_time == ''


def test_read_line_of_equals_signs_does_not_change_state():
    file_wrapper = FakeFileReadWrapper('===========================\n')
    my_transform = Transform(file_wrapper)
    my_transform.read_each_line()
    assert my_transform.last_date == ''
    assert my_transform.last_sleep_time == ''


def test_read_good_date_sets_last_date():
    file_wrapper = FakeFileReadWrapper('    2017-01-02\n')
    my_transform = Transform(file_wrapper)
    my_transform.read_each_line()
    assert my_transform.last_date == '2017-01-02'


def test_read_date_b_action_date_w_action_sets_last_sleep_time():
    file_wrapper = FakeFileReadWrapper('    2016-12-07\n'
                                       'action: b, time: 23:45\n'
                                       '    2016-12-08\n'
                                       'action: w, time: 3:45, hours: 4.00\n'
                                       )
    my_transform = Transform(file_wrapper)
    my_transform.read_each_line()
    assert my_transform.last_sleep_time == '23:45'


# note: reading a bad line now writes to do_transform.log instead of raising
# def test_read_bad_line_raises_indexerror():
#     with pytest.raises(IndexError):
#         file_wrapper = FakeFileReadWrapper('bongobongobongobongo')
#         my_transform = Transform(file_wrapper)
#         my_transform.read_each_line()
