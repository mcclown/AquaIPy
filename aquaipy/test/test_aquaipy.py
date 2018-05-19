import pytest
import requests
from aquaipy import AquaIPy, Response


def test_AquaIPy_init_raises_InvalidURL():
    with pytest.raises(requests.exceptions.InvalidURL):
        api = AquaIPy()
        api.connect("")


def test_AquaIPy_init_raises_ConnectionError():
    with pytest.raises(requests.exceptions.ConnectionError):
        api = AquaIPy()
        api.connect("mcclown.org")


