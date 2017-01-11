# file: test_lines_to_days.py
# andrew jarcho
# 2016-01-08

# python: 3.5


from datetime import date
import unittest
from unittest import TestCase

from lines_to_days import Event, Day


class TestEvent(TestCase):

    def test___init___raises_ValueError_if_segment_len_gt_3(self):
        segment = ['w', '12:45', 3.75, 'bongo']
        with self.assertRaises(ValueError):
            my_event = Event(segment)

    def test___init___raises_ValueError_if_segment_len_lt_3(self):
        segment = ['s', '23:30']
        with self.assertRaises(ValueError):
            my_event = Event(segment)

    def test___init___creates_valid_Event_with_valid_input_segment(self):
        segment = ['b', '0:00', 7.50]
        my_event = Event(segment)
        self.assertEqual(my_event.action, 'b')
        self.assertEqual(my_event.mil_time, '0:00')
        self.assertEqual(my_event.hours, 7.50)

    def test___init___creates_valid_Event_with_valid_hours_empty_input_segment(self):
        segment = ['s', '13:15', 0.00]
        my_event = Event(segment)
        self.assertEqual(my_event.action, 's')
        self.assertEqual(my_event.mil_time, '13:15')
        self.assertEqual(my_event.hours, 0.00)

    def test___str___returns_valid_string_on_valid_input_segment(self):
        segment = ['b', '0:45', 6.30]
        my_event = Event(segment)
        my_string = my_event.__str__()
        self.assertEqual(my_string, 'action: b, time: 0:45, hours: 6.30\n')

    def test___str___returns_valid_string_on_valid_short_input_segment(self):
        segment = ['s', '11:15',0.00]
        my_event = Event(segment)
        my_string = my_event.__str__()
        self.assertEqual(my_string, 'action: s, time: 11:15, hours: 0.00\n')


class TestDay(TestCase):

    def setUp(self):
        self.my_day = Day(date(2017, 1, 9))

    def test_Day_has_a_datetime_dt_date_member(self):
        self.assertIsInstance(self.my_day.dt_date, date)

    def test_Day_member_events_is_an_empty_list(self):
        self.assertIsInstance(self.my_day.events, list)
        self.assertEqual(len(self.my_day.events), 0)

    def test_calling_add_event_with_non_event_argument_raises_TypeError(self):
        with self.assertRaises(TypeError):
            self.my_day.add_event([1, 2, 3])

    def test_calling_add_event_with_event_argument_adds_item_to_events_list(self):
        self.my_day.add_event(Event(['s', '23:45', 1.00]))
        self.assertEqual(len(self.my_day.events), 1)
