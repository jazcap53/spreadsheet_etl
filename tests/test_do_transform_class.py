# file: tests/test_do_transform_class.py
# andrew jarcho
# 2017-03-15

# pytest 3.0.7


import pytest

from tests.file_access_wrappers import FakeFileReadWrapper
from src.transform.do_transform_class import Transform


def test_read_blank_line_does_not_change_state():
    file_wrapper = FakeFileReadWrapper('\n')
    open_file_wrapper = file_wrapper.open()
    my_transform = Transform(open_file_wrapper)
    my_transform.read_each_line()
    assert my_transform.last_date == ''
    assert my_transform.last_sleep_time == ''


def test_read_Week_of_line_does_not_change_state():
    file_wrapper = FakeFileReadWrapper('Week of Sunday, 2016-12-04:\n')
    open_file_wrapper = file_wrapper.open()
    my_transform = Transform(open_file_wrapper)
    my_transform.read_each_line()
    assert my_transform.last_date == ''
    assert my_transform.last_sleep_time == ''


def test_read_line_of_equals_signs_does_not_change_state():
    file_wrapper = FakeFileReadWrapper('===========================\n')
    open_file_wrapper = file_wrapper.open()
    my_transform = Transform(open_file_wrapper)
    my_transform.read_each_line()
    assert my_transform.last_date == ''
    assert my_transform.last_sleep_time == ''


def test_read_good_date_sets_last_date():
    file_wrapper = FakeFileReadWrapper('    2017-01-02\n')
    open_file_wrapper = file_wrapper.open()
    my_transform = Transform(open_file_wrapper)
    my_transform.read_each_line()
    assert my_transform.last_date == '2017-01-02'


def test_read_date_b_action_date_w_action_sets_last_sleep_time():
    file_wrapper = FakeFileReadWrapper('    2016-12-07\naction: b, time: 23:45\n'
                   '    2016-12-08\naction: w, time: 3:45, hours: 4.00\n'
                   )
    open_file_wrapper = file_wrapper.open()
    my_transform = Transform(open_file_wrapper)
    my_transform.read_each_line()
    assert my_transform.last_sleep_time == '23:45'


def test_read_bad_line_raises_IndexError():
    with pytest.raises(IndexError):
        file_wrapper = FakeFileReadWrapper('bongobongobongobongo')
        open_file_wrapper = file_wrapper.open()
        my_transform = Transform(open_file_wrapper)
        my_transform.read_each_line()
