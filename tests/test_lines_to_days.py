# file: test_lines_to_days.py
# andrew jarcho
# 2016-01-08

# python: 3.5


from datetime import date
import unittest
from unittest import TestCase

from lines_to_days import Event, DayLabel, Day


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


class TestDayLabel(TestCase):

    def test___init___raises_AssertionError_on_weekday_input_lt_0(self):
        with self.assertRaises(AssertionError):
            my_day_label = DayLabel(-1, date.today())

    def test___init___raises_AssertionError_on_weekday_input_gt_6(self):
        with self.assertRaises(AssertionError):
            my_day_label = DayLabel(7, date.today())

    def test___init___creates_valid_DayLabel_on_valid_input(self):
        my_day_label = DayLabel(1, date(2017, 1, 9))
        self.assertEqual(my_day_label.weekday, 'Monday')
        self.assertEqual(my_day_label.dt_date, date(2017, 1, 9))

    def test___str___returns_correct_string(self):
        my_day_label = DayLabel(3, date(2017, 1, 4))
        self.assertEqual(my_day_label.__str__(), 'Wednesday 2017-01-04')


class TestDay(TestCase):

    def setUp(self):
        self.my_day = Day(date(2017, 1, 9), 1)

    def test_Day_member_day_label_is_an_instance_of_DayLabel(self):
        self.assertIsInstance(self.my_day.day_label, DayLabel)

    def test_Day_member_day_label_has_a_string_weekday_and_a_datetime_date(self):
        self.assertIsInstance(self.my_day.day_label.weekday, str)
        self.assertIsInstance(self.my_day.day_label.dt_date, date)

    def test_Day_member_day_label_dot_weekday_is_a_valid_week_day_string(self):
        self.assertIn(self.my_day.day_label.weekday, DayLabel.week)

    def test_Day_member_events_is_an_empty_list(self):
        self.assertIsInstance(self.my_day.events, list)
        self.assertEqual(len(self.my_day.events), 0)

    def test_calling_add_event_with_non_event_argument_raises_AssertionError(self):
        with self.assertRaises(AssertionError):
            self.my_day.add_event([1, 2, 3])

    def test_calling_add_event_with_event_argument_adds_item_to_events_list(self):
        self.my_day.add_event(Event(['s', '23:45', 1.00]))
        self.assertEqual(len(self.my_day.events), 1)





