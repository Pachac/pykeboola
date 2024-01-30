import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def pytest_addoption(parser):
    parser.addoption("--token", action="store")


@pytest.fixture(scope='session')
def token(request):
    token_value = request.config.option.token
    if token_value is None:
        pytest.skip()
    return token_value

URL = 'https://connection.eu-central-1.keboola.com/'
JOB_ID_ERROR = 676624983
JOB_ID_SUCCESS = 676625356
