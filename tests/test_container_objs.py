# file: test/test_container_objs.py
# andrew jarcho
# 2016-01-08

# nosetests: 1.3.7


from datetime import date, timedelta
import unittest
from unittest import TestCase
import io

from extract.container_objs import validate_segment, Event, Day, Week
from extract.container_objs import print_event


class TestValidateSegment(TestCase):

    def test_empty_segment_returns_false(self, seg=['', '', '']):
        self.assertFalse(validate_segment(seg))

    def test_non_null_segment_and_not_item_0_returns_false(self, seg=['', '4:15', '']):
        self.assertFalse(validate_segment(seg))

    def test_first_char_of_item_0_is_not_valid_returns_false(self, seg=['x', '11:30', '2.50']):
        self.assertFalse(validate_segment(seg))

    def test_extra_space_in_item_0_returns_true(self, seg=['b ', '22:45', '7.50']):
        self.assertTrue(validate_segment(seg))

    def test_item_0_is_s_and_item_2_is_not_blank_returns_false(self, seg=['s', '10:00', '1.00']):
        self.assertFalse(validate_segment(seg))

    def test_item_0_is_w_and_item_2_is_blank_returns_false(self, seg=['w', '0:00', '']):
        self.assertFalse(validate_segment(seg))

    def test_item_2_is_not_blank_and_does_not_match_regex_returns_false(self, seg=['w', '1:00', '1.a5']):
        self.assertFalse(validate_segment(seg))


class TestEvent(TestCase):

    def test_Event_ctor_raises_TypeError_if_segment_len_gt_3(self):
        segment = ['w', '12:45', '3.75', 'bongo']
        with self.assertRaises(TypeError):
            my_event = Event(*segment)

    def test_Event_ctor_raises_TypeError_if_segment_len_lt_3(self):
        segment = ['s', '23:30']
        with self.assertRaises(TypeError):
            my_event = Event(*segment)

    def test_Event_ctor_creates_valid_Event_with_valid_input_segment(self):
        segment = ['b', '0:00', '7.50']
        my_event = Event(*segment)
        self.assertEqual(my_event.action, 'b')
        self.assertEqual(my_event.mil_time, '0:00')
        self.assertEqual(my_event.hours, '7.50')

    def test_Event_ctor_creates_valid_Event_with_valid_hours_empty_input_segment(self):
        segment = ['s', '13:15', '']
        my_event = Event(*segment)
        self.assertEqual(my_event.action, 's')
        self.assertEqual(my_event.mil_time, '13:15')
        self.assertEqual(my_event.hours, '')

    def test_print_event_outputs_valid_string_on_valid_input_segment(self):
        segment = ['b', '0:45', '6.30']
        my_event = Event(*segment)
        my_output = io.StringIO()
        print_event(my_event, my_output)
        my_string = my_output.getvalue()
        self.assertEqual(my_string, u'action: b, time: 0:45, hours: 6.30\n')

    def test_print_event_outputs_valid_string_on_valid_short_input_segment(self):
        segment = ['s', '11:15', '']
        my_event = Event(*segment)
        my_output = io.StringIO()
        print_event(my_event, my_output)
        my_string = my_output.getvalue()
        self.assertEqual(my_string, u'action: s, time: 11:15\n')


class TestDay(TestCase):

    def setUp(self):
        self.my_day = Day(date(2017, 1, 9), [])

    def test_Day_has_a_datetime_dt_date_member(self):
        self.assertIsInstance(self.my_day.dt_date, date)

    def test_Day_member_events_starts_as_an_empty_list(self):
        self.assertIsInstance(self.my_day.events, list)
        self.assertEqual(len(self.my_day.events), 0)

    def test_appending_event_to_Day_dot_events_is_successful(self):
        self.my_day.events.append(Event('s', '23:45', ''))
        self.assertEqual(len(self.my_day.events), 1)

    def test_creating_an_empty_event_raises_ValueError(self):
        with self.assertRaises(ValueError):
            self.my_day.events.append(Event('', '', ''))

    def test_creating_a_bad_event_raises_ValueError(self):
        with self.assertRaises(ValueError):
            self.my_day.events.append(Event('x', '4:00', '1.75'))


class TestWeek(TestCase):

    def setUp(self):
        dts = [Day(date(2017, 1, 15) + timedelta(days=x), [])
                for x in range(7)]
        self.my_week = Week(*dts)

    def test_initializing_Week_with_non_Sunday_date_raises_ValueError(self):
        dts = [Day(date(2017, 1, 14) + timedelta(days=x), [])
                for x in range(7)]
        with self.assertRaises(ValueError):
            self.my_other_week = Week(*dts)

    def test_first_day_of_Week_is_Sunday(self):
        self.assertEqual(self.my_week[0].dt_date.weekday(), 6)

    def test_a_Week_has_seven_Days(self):
        self.assertEqual(len(self.my_week), 7)

    def test_days_two_thru_seven_of_Week_have_no_Sunday(self):
        # f checks that day x is a Sunday
        f = lambda x: self.my_week[x].dt_date.weekday() == 6
        self.assertFalse(any(f(x) for x in range(1, 7)))
