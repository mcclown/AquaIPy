import pytest
from aquaipy.test import ENDPOINT_CONFIG_NAME

def pytest_addoption(parser):
        parser.addini(ENDPOINT_CONFIG_NAME, 'The endpoint to use for testing.')

