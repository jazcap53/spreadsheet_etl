# file: src/purge_fns.py
# andrew jarcho
# 2017-01-27

# python: 2.7, 3.5


from __future__ import print_function

import datetime
from datetime import date
import re
import sys

from container_objs import print_event, weeks
from spreadsheet_etl.tests.file_access_wrappers import FileReadAccessWrapper


def purge(weeks, out=sys.stdout):
    """
    Called by: client code
    """
    purging = True
    event = None
    final_event = _get_final_event(weeks)
    if final_event:  # None or a 4-tuple
        week_ix, day_ix, event_ix, event = final_event
    while event:
        if purging:
            if _stops_purge(event):
                purging = False
            else:
                if __debug__:
                    out.write('popping ')
                    print_event(event, out)
                weeks[week_ix][day_ix].events.pop(event_ix)
        else:
            if _restarts_purge(event):
                purging = True
            else:
                if __debug__:
                    out.write('keeping ')
                    print_event(event, out)
        previous_event = _get_previous_event(weeks, week_ix, day_ix, event_ix, out)
        if previous_event:  # None or a 4-tuple
            week_ix, day_ix, event_ix, event = previous_event
        else:
            event = None
    return weeks


def _get_final_event(weeks):
    """
    Called by: purge()
    """
    week_ix = _get_final_nonempty_week(weeks)
    if week_ix is not None:
        day_ix = _get_final_nonempty_day(weeks, week_ix)
        event_ix = len(weeks[week_ix][day_ix].events) - 1
        event = weeks[week_ix][day_ix].events[event_ix]
        return (week_ix, day_ix, event_ix, event)
    return None


def _get_final_nonempty_week(weeks):
    """
    Called by: _get_final_event()
    """
    week_ix = len(weeks) - 1
    while week_ix > -1 and _week_is_empty(weeks, week_ix):
        week_ix -= 1
    return None if week_ix == -1 else week_ix


def _week_is_empty(weeks, week_ix):
    """
    Called by: _get_final_nonempty_week()
    """
    return all([_day_is_empty(weeks, week_ix, d) for d in range(7)])


def _day_is_empty(weeks, week_ix, day_ix):
    """
    Called by: _week_is_empty(), _get_final_nonempty_day(),
               _get_previous_nonempty_day()
    """
    return not len(weeks[week_ix][day_ix].events)


def _get_final_nonempty_day(weeks, week_ix):
    """
    Called by: _get_final_event()
    param: week_ix is a non-None return value from _get_final_nonempty_week()
    returns: integer between 0 and 6 inclusive
    """
    day_ix = 6
    while day_ix and _day_is_empty(weeks, week_ix, day_ix):
        day_ix -= 1
    return day_ix


def _stops_purge(event):
    """
    Called by: purge()
    """
    if event is None:
        return True
    return event.action == 'b' and event.mil_time and event.hours


def _get_previous_event(weeks, week_ix, day_ix, event_ix, out):
    """
    Called by: purge()
    pre: week_ix, day_ix, event_ix are not None
    """
    ret_val = None
    if event_ix:
        event_ix -= 1
        event = weeks[week_ix][day_ix].events[event_ix]
    else:
        week_ix, day_ix = _get_previous_nonempty_day(weeks, week_ix, day_ix)
        if week_ix is not None:  # there was a previous nonempty day
            event_ix = len(weeks[week_ix][day_ix].events) - 1
            if __debug__:
                out.write('week: {}, day: {}, event: {}\n'.format(week_ix, day_ix, event_ix))
            event = weeks[week_ix][day_ix].events[event_ix]
    if week_ix is not None:
        ret_val = week_ix, day_ix, event_ix, event
    return ret_val


def _restarts_purge(event):
    """
    Called by: purge()
    """
    return event.action == 'b' and (not event.mil_time or not event.hours)


def _get_previous_day(week_ix, day_ix):
    """
    Called by: _get_previous_nonempty_day()
    """
    if day_ix:
        day_ix -= 1
    else:
        if week_ix:
            week_ix -= 1
            day_ix = 6
        else:  # we were already on day 0 of week 0
            return (None, None)
    return week_ix, day_ix


def _get_previous_nonempty_day(weeks, week_ix, day_ix):
    """
    Called by: _get_previous_event()
    """
    week_ix, day_ix = _get_previous_day(week_ix, day_ix)
    while week_ix is not None and _day_is_empty(weeks, week_ix, day_ix):
        week_ix, day_ix = _get_previous_day(week_ix, day_ix)
    return week_ix, day_ix
