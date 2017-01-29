# file: purge_fns.py
# andrew jarcho
# 2017-01-27

# python: 2.7, 3.5


from __future__ import print_function

import datetime
from datetime import date
import re
import sys

from container_objs import Event, Week
from spreadsheet_etl.tests.file_access_wrappers import FileReadAccessWrapper


def week_is_empty(weeks, week_ix):
    return all([day_is_empty(weeks, week_ix, d) for d in range(7)])


def day_is_empty(weeks, week_ix, day_ix):
    return not len(weeks[week_ix].day_list[day_ix].events)


def restarts_purge(event):
    return event.action == 'b' and (not event.mil_time or not event.hours)


def stops_purge(event):
    if event is None:
        return True
    return event.action == 'b' and event.mil_time and event.hours


def purge(weeks):
    purging = True
    event = None
    final_event = get_final_event(weeks)
    if final_event:  # None or a 4-tuple
        week_ix, day_ix, event_ix, event = final_event
    while event:
        if purging:
            if stops_purge(event):
                purging = False
            else:
                if __debug__:
                    print('popping {}'.format(event))
                weeks[week_ix].day_list[day_ix].events.pop(event_ix)
        else:
            if restarts_purge(event):
                purging = True
            else:
                if __debug__:
                    print('keeping {}'.format(event))
        previous_event = get_previous_event(weeks, week_ix, day_ix, event_ix)
        if previous_event:  # None or a 4-tuple
            week_ix, day_ix, event_ix, event = previous_event
        else:
            event = None
    return weeks


def get_final_event(weeks):
    week_ix = get_final_nonempty_week(weeks)
    if week_ix is not None:
        day_ix = get_final_nonempty_day(weeks, week_ix)
        event_ix = len(weeks[week_ix].day_list[day_ix].events) - 1
        event = weeks[week_ix].day_list[day_ix].events[event_ix]
        return (week_ix, day_ix, event_ix, event)
    return None


def get_previous_event(weeks, week_ix, day_ix, event_ix):
    """
    pre: week_ix, day_ix, event_ix are not None
    """
    ret_val = None
    if event_ix:
        event_ix -= 1
        event = weeks[week_ix].day_list[day_ix].events[event_ix]
    else:
        week_ix, day_ix = get_previous_nonempty_day(weeks, week_ix, day_ix)
        if week_ix is not None:  # there was a previous nonempty day
            event_ix = len(weeks[week_ix].day_list[day_ix].events) - 1
            if __debug__:
                print('week: {}, day: {}, event: {}'.format(week_ix, day_ix, event_ix))
            event = weeks[week_ix].day_list[day_ix].events[event_ix]
    if week_ix is not None:
        ret_val = week_ix, day_ix, event_ix, event
    return ret_val


def get_final_nonempty_week(weeks):
    week_ix = len(weeks) - 1
    while week_ix > -1 and week_is_empty(weeks, week_ix):
        week_ix -= 1
    return None if week_ix == -1 else week_ix


def get_final_nonempty_day(weeks, week_ix):
    """
    param: week_ix is a non-None return value from get_final_nonempty_week()
    returns: integer between 0 and 6 inclusive
    """
    day_ix = 6
    while day_ix and day_is_empty(weeks, week_ix, day_ix):
        day_ix -= 1
    return day_ix


def get_previous_day(week_ix, day_ix):
    if day_ix:
        day_ix -= 1
    else:
        if week_ix:
            week_ix -= 1
            day_ix = 6
        else:  # we were already on day 0 of week 0
            return (None, None)
    return week_ix, day_ix


def get_previous_nonempty_day(weeks, week_ix, day_ix):
    week_ix, day_ix = get_previous_day(week_ix, day_ix)
    while week_ix is not None and day_is_empty(weeks, week_ix, day_ix):
        week_ix, day_ix = get_previous_day(week_ix, day_ix)
    return week_ix, day_ix
