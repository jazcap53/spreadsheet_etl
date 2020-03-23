import pytest
import os
import sys
from sqlalchemy import create_engine


@pytest.fixture(scope='module')
def url():
    try:
        db_url = os.environ['DB_URL_TEST']
    except KeyError:
        print('Please set environment variable DB_URL_TEST')
        sys.exit(1)
    yield db_url


@pytest.fixture(scope='module')
def cnxn(url):
    engine = create_engine(url)
    cnxn = engine.connect()
    yield cnxn
    cnxn.close()


@pytest.fixture
def cursor(cnxn):
    cursor = cnxn.cursor()
    yield cursor
    cnxn.rollback()
