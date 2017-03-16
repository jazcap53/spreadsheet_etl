# file: tests/test_do_transform.py
# andrew jarcho
# 2017-03-15

# nosetests 1.3.7

import unittest
from unittest import TestCase

from src.transform.do_transform import process_curr


class TestDoTransform(TestCase):

    def setUp(self):
        self.p_c = process_curr()

    def test_nada(self):
        self.assertTrue(True)
