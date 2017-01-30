# file: tests/file_access_wrappers.py
# author: Andrew Jarcho
# date: 2017-01-22

# python: 3.x

import io


class FileReadAccessWrapper:

    def __init__(self, filename):
        self.filename = filename

    def open(self):
        return open(self.filename, 'r')


class FakeFileWrapper:
    def __init__(self, text):
        self.text = text

    def open(self):
        return io.StringIO(self.text)