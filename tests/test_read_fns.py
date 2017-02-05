# file: tests/test_read_fns.py
# andrew jarcho
# 2017-01-28

# python: 3.5  TODO: check this, 2.7, and nosetests

import io

import datetime
import unittest
from unittest import TestCase

from tests.file_access_wrappers import FakeFileWrapper
from src.read_fns import open_file, read_lines, is_header, store_week
from src.read_fns import check_for_date
from src.container_objs import Week


# TODO: make sure all tests make sense, and pass
class TestReadFns(TestCase):

    def setUp(self):
        self.file_wrapper = FakeFileWrapper(
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
        self.weeks = []

    def test_open_file(self):
        self.infile = open_file(self.file_wrapper)
        self.assertIsInstance(self.infile, io.StringIO)

    def test_read_lines_stores_one_week(self):
        self.infile = open_file(self.file_wrapper)
        self.weeks = read_lines(self.infile, self.weeks)
        self.assertEqual(len(self.weeks), 1)

    def test_is_header_returns_true_for_header_line(self):
        self.infile = open_file(self.file_wrapper)
        line = self.infile.readline().strip().split(',')
        self.assertTrue(is_header(line))

    def test_is_header_returns_false_for_non_header_line(self):
        self.infile = open_file(self.file_wrapper)
        line = self.infile.readline().strip().split(',')
        line = self.infile.readline().strip().split(',')
        self.assertFalse(is_header(line))

    @unittest.skip
    def test_store_week_appends_week_to_week_list(self):
        sunday_date = datetime.date(2016, 12, 4)
        have_unstored_event = True
        old_weeks = self.weeks[:]
        new_week = Week(sunday_date)
        self.weeks, sunday_date, have_unstored_event, new_week = store_week(
                self.weeks, sunday_date, have_unstored_event, new_week)
        self.assertEqual(len(self.weeks), len(old_weeks) + 1)

    def test_check_for_date_matches_date_in_correct_format(self):
        date_string = '12/34/5678'
        good_match = check_for_date(date_string)
        self.assertTrue(good_match)

    def test_check_for_date_rejects_date_with_hyphens(self):
        date_string = '12-34-5678'
        good_match = check_for_date(date_string)
        self.assertFalse(good_match)

    def test_check_for_date_rejects_date_with_alpha(self):
        date_string = 'a2/34/5678'
        good_match = check_for_date(date_string)
        self.assertFalse(good_match)

