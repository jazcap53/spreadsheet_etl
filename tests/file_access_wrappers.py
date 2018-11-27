# file: tests/file_access_wrappers.py
# author: Andrew Jarcho
# date: 2017-01-22

# python: 3.5  pytest: 3.0.7

import io


class FileReadAccessWrapper:

    def __init__(self, filename):
        self.filename = filename

    def open(self):
        return open(self.filename, 'r')

    def readline(self):
        for line in self.open():
            yield line[:-1]


class FakeFileReadWrapper:
    def __init__(self, text):
        self.text = text

    def open(self):
        return io.StringIO(self.text)

    def input(self):
        for line in self.open().readline():
            yield line[:-1]

