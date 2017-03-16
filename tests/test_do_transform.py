# file: tests/test_do_transform.py
# andrew jarcho
# 2017-03-15

# pytest 3.0.7


import pytest

from src.transform.do_transform import process_curr


@pytest.fixture
def inner_process_curr():
    return process_curr()


def test_nada(inner_process_curr):
    cur_l = '    2017-01-12'
    inner_process_curr(cur_l)
    assert True


