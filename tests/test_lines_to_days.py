# file: test_lines_to_days.py
# andrew jarcho
# 2016-01-08

# python: 2.7, 3.5


from datetime import date
import unittest
from unittest import TestCase

from lines_to_days import Event, Day, Week


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
        segment = ['s', '13:15', '']
        my_event = Event(segment)
        self.assertEqual(my_event.action, 's')
        self.assertEqual(my_event.mil_time, '13:15')
        self.assertIsNone(my_event.hours)

    def test___str___returns_valid_string_on_valid_input_segment(self):
        segment = ['b', '0:45', 6.30]
        my_event = Event(segment)
        my_string = my_event.__str__()
        self.assertEqual(my_string, 'action: b, time: 0:45, hours: 6.30')

    def test___str___returns_valid_string_on_valid_short_input_segment(self):
        segment = ['s', '11:15', '']
        my_event = Event(segment)
        my_string = my_event.__str__()
        self.assertEqual(my_string, 'action: s, time: 11:15')


class TestDay(TestCase):

    def setUp(self):
        self.my_day = Day(date(2017, 1, 9))

    def test_Day_has_a_datetime_dt_date_member(self):
        self.assertIsInstance(self.my_day.dt_date, date)

    def test_Day_member_events_starts_as_an_empty_list(self):
        self.assertIsInstance(self.my_day.events, list)
        self.assertEqual(len(self.my_day.events), 0)

    def test_calling_add_event_with_non_event_argument_raises_TypeError(self):
        with self.assertRaises(TypeError):
            self.my_day.add_event([1, 2, 3])

    def test_calling_add_event_with_event_argument_adds_item_to_events_list(self):
        self.my_day.add_event(Event(['s', '23:45', 1.00]))
        self.assertEqual(len(self.my_day.events), 1)


class TestWeek(TestCase):

    def setUp(self):
        self.my_week = Week(date(2017, 1, 15))

    def test_calling___init___with_non_Sunday_date_raises_ValueError(self):
        with self.assertRaises(ValueError):
            self.my_other_week = Week(date(2017, 1, 14))

    def test_first_day_of_Week_is_Sunday(self):
        self.assertEqual(self.my_week.day_list[0].dt_date.weekday(), 6)

    def test_a_Week_has_seven_Days(self):
        self.assertEqual(len(self.my_week.day_list), 7)

    def test_days_two_thru_seven_of_Week_have_no_Sunday(self):
        # f checks that day x is a Sunday
        f = lambda x: self.my_week.day_list[x].dt_date.weekday() == 6
        self.assertFalse(any(f(x) for x in range(1, 7)))













