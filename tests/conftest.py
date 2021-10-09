import argparse
import pytest
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker

Session = sessionmaker(autoflush=False)


@pytest.fixture(scope='module')
def url():
    try:
        db_url = os.environ['DB_URL_TEST']
    except KeyError:
        print('Please set environment variable DB_URL_TEST')
        sys.exit(1)
    yield db_url


@pytest.fixture(scope='module')
def session(url):
    engine = create_engine(url)
    cnxn = engine.connect()
    Session.configure(bind=cnxn)
    sess = Session()
    yield sess
    sess.rollback()
    cnxn.close()


@pytest.fixture
def args_d():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug_chart')
    return parser.parse_args()
