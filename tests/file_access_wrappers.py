# file: tests/file_access_wrappers.py
# author: Andrew Jarcho
# date: 2017-01-22

# python: 3.5  pytest: 3.0.7

import io


class FileReadAccessWrapper:

    def __init__(self, infilename):
        self.infilename = infilename

    def open(self):
        return open(self.infilename, 'r')


class FileWriteAccessWrapper:  # TODO: not in use

    def __init__(self, outfilename):
        self.outfilename = outfilename

    def open(self):
        return open(self.outfilename, 'w')


class FakeFileReadWrapper:
    def __init__(self, text, debug=False, infilename=None, outfilename=None):
        self.text = text
        self.start_ix = 0
        self.debug = debug
        self.infilename=infilename
        self.outfilename=outfilename

    def open(self):
        return io.StringIO(self.text)

    def input(self):
        return self.open()

    def __iter__(self):  # TODO: not in use -- needs testing
        return self

    def __next__(self):  # TODO: not in use -- needs testing
        next_newline_ix = self.text.find('\n', self.start_ix)
        if next_newline_ix == -1:
            raise StopIteration
        else:
            ret_str = self.text[self.start_ix: next_newline_ix]
            self.start_ix = next_newline_ix + 1
            return ret_str
