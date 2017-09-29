# file: tests/test_read_fns.py
# andrew jarcho
# 2017-01-28

# pytest 3.0.7

import io
# from collections import namedtuple
# import datetime
import pytest

from tests.file_access_wrappers import FakeFileReadWrapper
from src.extract.read_fns import open_file, read_lines
from src.extract.read_fns import _check_for_date
# from src.extract.container_objs import Week, Day


@pytest.fixture
def file_wrapper():
    return FakeFileReadWrapper(
                u''',Sun,,,Mon,,,Tue,,,Wed,,,Thu,,,Fri,,,Sat,,
12/4/2016,,,,,,,,,,b,23:45,,w,3:45,4.00,w,2:00,2.75,b,0:00,9.00
,,,,,,,,,,,,,s,4:45,,s,3:30,,w,5:15,5.25
,,,,,,,,,,,,,w,6:15,1.50,w,8:45,5.25,s,10:30,
,,,,,,,,,,,,,s,11:30,,s,19:30,,w,11:30,1.00
,,,,,,,,,,,,,w,12:15,0.75,w,20:30,1.00,s,16:00,
,,,,,,,,,,,,,s,16:45,,,,,w,17:00,1.00
,,,,,,,,,,,,,w,17:30,0.75,,,,b,22:30,7.25
,,,,,,,,,,,,,s,21:00,,,,,,,
,,,,,,,,,,,,,w,21:30,0.50,,,,,,
,,,,,,,,,,,,,b,23:15,7.50,,,,,,
,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,
''')


def test_open_file(file_wrapper):
    infile = open_file(file_wrapper)
    assert isinstance(infile, io.StringIO)


def test_read_lines_stores_one_week(file_wrapper):
    weeks = []
    infile = open_file(file_wrapper)
    weeks = read_lines(infile, weeks)
    assert len(weeks) == 1


def test__check_for_date_matches_date_in_correct_format(file_wrapper):
    date_string = '12/34/5678'
    good_match = _check_for_date(date_string)
    assert good_match


def test__check_for_date_rejects_date_with_hyphens(file_wrapper):
    date_string = '12-34-5678'
    good_match = _check_for_date(date_string)
    assert not good_match


def test__check_for_date_rejects_date_with_alpha(file_wrapper):
    date_string = 'a2/34/5678'
    good_match = _check_for_date(date_string)
    assert not good_match
