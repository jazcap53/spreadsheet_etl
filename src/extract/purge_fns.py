# file: src/extract/purge_fns.py
# andrew jarcho
# 2017-01-27

# python: 3.5


"""
Removes any incomplete Day's from the weeks list.

A Day is 'incomplete' if the data do not show the total hours slept
during that Day. Each 'b' event holds the total hours slept in the
previous Day as its third element *if that total is known*. Thus a
'b' event with fewer than 3 elements indicates that some sleep data
from the preceding Day are missing.

purge() reads Event's in reverse order from the last Event to the first.
Reading a complete (3-element) 'b' event stops the purging.
Reading an incomplete (less than 3-element) 'b' event restarts the purging.

purge() controls the data processing: all other functions in this file are
called from purge() 
"""

import sys


def purge(weeks, out=sys.stdout):
    """
    Remove incomplete Day's from the weeks list. Processing begins with
        the last Event and proceeds backwards to the first Event.
    
    Returns: the weeks list, with the Event's from any incomplete Day's
             removed
    Called by: client code
    """
    purging = True
    event = None
    final_event = _get_final_event(weeks)
    if final_event:  # final_event is None or a 4-tuple
        week_ix, day_ix, event_ix, event = final_event
    while event:
        if purging:
            if _stops_purge(event):
                purging = False
            weeks[week_ix][day_ix].events.pop(event_ix)
        else:
            if _restarts_purge(event):
                purging = True
        previous_event = _get_previous_event(weeks, week_ix, day_ix, event_ix, out)
        if previous_event:  # final_event is None or a 4-tuple
            week_ix, day_ix, event_ix, event = previous_event
        else:
            event = None
    return weeks


def _get_final_event(weeks):
    """
    Get the last event, if any, in the weeks list.
    
    Returns: a 4-tuple specifying that event, or None
    Called by: purge()
    """
    week_ix = _get_final_nonempty_week(weeks)
    if week_ix is not None:
        day_ix = _get_final_nonempty_day(weeks, week_ix)
        event_ix = len(weeks[week_ix][day_ix].events) - 1
        event = weeks[week_ix][day_ix].events[event_ix]
        return week_ix, day_ix, event_ix, event
    return None


def _get_final_nonempty_week(weeks):
    """
    Get the last Week in the weeks list that has at least one 
        non-empty Day.
        
    Returns: the index into weeks of that last Week, or None
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
    param: week_ix is a non-None return value from 
           _get_final_nonempty_week()
    Returns: an integer between 0 and 6 inclusive representing the day
             of the week -- 0 is Sunday
    """
    day_ix = 6
    while day_ix and _day_is_empty(weeks, week_ix, day_ix):
        day_ix -= 1
    return day_ix


def _stops_purge(event):
    """
    Stops the purge when it encounters a complete 'b' Event or None
    
    Called by: purge()
    """
    if event is None:
        return True
    return event.action == 'b' and event.mil_time and event.hours


def _get_previous_event(weeks, week_ix, day_ix, event_ix, out):
    """
    Returns: a 4-tuple describing the preceding event, or None if there
             is no such event
    Called by: purge()
    pre: week_ix, day_ix, event_ix are not None
    """
    ret_val = None
    event = None
    if event_ix:  # index into current Day's Event list
        event_ix -= 1
        event = weeks[week_ix][day_ix].events[event_ix]
    else:
        week_ix, day_ix = _get_previous_nonempty_day(weeks, week_ix, day_ix)
        if week_ix is not None:  # there was a previous nonempty day
            event_ix = len(weeks[week_ix][day_ix].events) - 1
            event = weeks[week_ix][day_ix].events[event_ix]
    if week_ix is not None:
        ret_val = week_ix, day_ix, event_ix, event
    return ret_val


def _restarts_purge(event):
    """
    Returns: bool -- is event parameter an incomplete 'b' event    
    Called by: purge()
    """
    return event.action == 'b' and (not event.mil_time or not event.hours)


def _get_previous_nonempty_day(weeks, week_ix, day_ix):
    """
    Returns: a 2-tuple describing the previous non-empty day, if any
             else None, None
    Called by: _get_previous_event()
    """
    week_ix, day_ix = _get_previous_day(week_ix, day_ix)
    while week_ix is not None and _day_is_empty(weeks, week_ix, day_ix):
        week_ix, day_ix = _get_previous_day(week_ix, day_ix)
    return week_ix, day_ix


def _get_previous_day(week_ix, day_ix):
    """
    Returns: a 2-tuple describing the previous day, if any
             else None, None
    Called by: _get_previous_nonempty_day()
    """
    if day_ix:
        day_ix -= 1
    else:  # there's no previous Day this week: check previous Week
        if week_ix:
            week_ix -= 1
            day_ix = 6
        else:  # we were already on day 0 of week 0
            return None, None
    return week_ix, day_ix
