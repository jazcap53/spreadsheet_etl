# file: test_lines_to_days.py
# andrew jarcho
# 2016-01-08

# python: 3.5


import unittest
from unittest import TestCase

from lines_to_days import Event


class TestEvent(TestCase):

    def test___init___raises_AssertionError_if_segment_len_gt_3(self):
        segment = ['w', '12:45', 3.75, 'bongo']
        with self.assertRaises(AssertionError):
            my_event = Event(segment)

    def test___init___raises_AssertionError_if_segment_len_lt_3(self):
        segment = ['s', '23:30']
        with self.assertRaises(AssertionError):
            my_event = Event(segment)

    def test___init___creates_valid_Event_with_valid_input_segment(self):
        segment = ['b', '0:00', 7.50]
        my_event = Event(segment)
        self.assertEqual(my_event.action, 'b')
        self.assertEqual(my_event.mil_time, '0:00')
        self.assertEqual(my_event.hours, 7.50)

    def test___init___creates_valid_Event_with_valid_hours_empty_input_segment(self):
        segment = ['s', '13:15', '']
        my_event = Event(segment)
        self.assertEqual(my_event.action, 's')
        self.assertEqual(my_event.mil_time, '13:15')
        self.assertEqual(my_event.hours, '')

    def test___str___returns_valid_string_on_valid_input_segment(self):
        segment = ['b', '0:45', 6.30]
        my_event = Event(segment)
        my_string = my_event.__str__()
        self.assertEqual(my_string, 'action: b, time: 0:45, hours: 6.30\n')

