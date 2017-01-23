# file: test_lines_to_days.py
# andrew jarcho
# 2016-01-08

# python: 2.7, 3.5


from datetime import date
import unittest
from unittest import TestCase

from spreadsheet_etl.src.lines_to_days import ReadAndPurge

class TestReadAndPurge(TestCase):

    def test_nothing(self):
        self.assertEqual(1, 1)


