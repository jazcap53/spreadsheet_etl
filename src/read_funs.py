from __future__ import print_function

import re
import datetime

from container_objs import Week, Event


def print_out(weeks):
    for week in weeks:
        print(week)
    print()


def open_file(file_read_wrapper):
    return file_read_wrapper.open()


def read_lines(infile, weeks, sunday_date=None, have_unstored_event=False,
        new_week=None):
    for line in infile:
        line = line.strip().split(',')
        if is_header(line):
            continue
        if not any(line):  # we had a blank row in the spreadsheet
            weeks, sunday_date, have_unstored_event, new_week = store_week(
                    weeks, sunday_date, have_unstored_event, new_week)
            continue
        if not sunday_date:
            found_match = check_for_date(line[0])
            if not found_match:  # we are not at the start of a week
                continue
            sunday_date = match_to_date_obj(found_match)
            new_week = Week(sunday_date)
        if any(line[1:]):
            have_unstored_event, new_week = load_line(line[1:], new_week)
    # save any left-over unstored data
    store_week(weeks, sunday_date, have_unstored_event, new_week)
    return weeks


def is_header(l):
    return l[1] == 'Sun'


def store_week(weeks, sunday_date, have_unstored_event, new_week):
    if sunday_date  and have_unstored_event and new_week:
        weeks.append(new_week)
        return weeks, None, False, None
    return weeks, sunday_date, have_unstored_event, new_week


def check_for_date(s):
    m = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', s)
    return m if m else None


def match_to_date_obj(m):
    # group(3) is the year, group(1) is the month, group(2) is the day
    d = [int(m.group(x)) for x in (3, 1, 2)]
    d_obj = datetime.date(d[0], d[1], d[2])
    return d_obj


def load_line(line, new_week):
    for ix in range(7):
        a_event = Event(line[3*ix: 3*ix + 3])
        if new_week and a_event.action:
            new_week.day_list[ix].add_event(a_event)
            have_unstored_event = True
    return have_unstored_event, new_week
