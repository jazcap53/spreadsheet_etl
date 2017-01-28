# file: test_lines_to_days.py
# andrew jarcho
# 2017-01-08

# python: 2.7, 3.5


from datetime import date
import unittest
from unittest import TestCase

from tests.file_access_wrappers import FakeFileWrapper
from src.lines_to_days import Read

class TestNothing(TestCase):

    def test_nothing(self):
        self.assertEqual(1, 1)


class TestRead(TestCase):

    def test___init___makes_a_Read_object(self):
        self.file_wrapper = FakeFileWrapper(
                '''
                ,Sun,,,Mon,,,Tue,,,Wed,,,Thu,,,Fri,,,Sat,,
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
        self.read_obj = Read(self.weeks, self.file_wrapper)
        self.assertIsInstance(self.read_obj, Read)
