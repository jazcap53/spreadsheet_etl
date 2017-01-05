# file: lines_to_days.py
# andrew jarcho
# 2017-01-05

# python: 3.5


import sys


class Line:
    def __init__(self, cells):
        self.cells = cells


class DayItem:
    def __init__(self, action, wall_time, elapsed):
        self.action = action
        self.wall_time = wall_time
        self.elapsed = elapsed


class Day:
    def __init__(self, date):
        self.date = date
        self.day_items = []

    def add_day_item(self, day_item):
        self.day_items.append(day_item)


class LinesToDays:
    def __init__(self, infile):
        self.infile = infile
        self.days = []
        self.sunday_date = None
        self.week_offset = None

    def convert(self):
        pass

    def readLines(self):
        for line in self.infile:
            with_commas = line
            no_commas = with_commas.split(',')
            if not any(no_commas):
                continue
            if self.is_date(no_commas[0]):  # self.is_date() -- N.Y.I.
                sun_date_string = no_commas[0]
                sun_date_list = sun_date_string.split('/')
                sun_date_obj = date(

            else:
                self.week_offset += 1
