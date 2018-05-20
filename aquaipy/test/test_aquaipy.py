import pytest
from unittest.mock import Mock, patch

import requests
from aquaipy import AquaIPy, Response
from aquaipy.test.TestData import TestData


def test_AquaIPy_init_raises_InvalidURL():
    
    with pytest.raises(requests.exceptions.InvalidURL):
        api = AquaIPy()
        api.connect("")


def test_AquaIPy_init_raises_ConnectionError():
    
    with pytest.raises(requests.exceptions.ConnectionError):
        api = AquaIPy()
        api.connect("mcclown.org")


def test_AquaIPy_init_with_name():

    api = AquaIPy("Test Name")

    assert api.name == "Test Name"

def test_AquaIPy_init_success():

    api = TestHelper.get_connected_instance()

    assert api.mac_addr == "D8976003AAAA"
    assert api.supported_firmware
    assert api.product_type == "Hydra TwentySix"
    assert api.name == None


def test_AquaIPy_get_schedule_state_enabled():

    api = TestHelper.get_connected_instance()

    with patch('aquaipy.aquaipy.requests.get') as mock_get:
        mock_get.return_value.json.return_value = TestData.schedule_enabled()

        assert api.get_schedule_state()


def test_AquaIPy_get_schedule_state_disabled():

    api = TestHelper.get_connected_instance()

    with patch('aquaipy.aquaipy.requests.get') as mock_get:
        mock_get.return_value.json.return_value = TestData.schedule_disabled()

        assert api.get_schedule_state() == False

def test_AquaIPy_get_raw_brightness_all_0():

    api = TestHelper.get_connected_instance()

    with patch('aquaipy.aquaipy.requests.get') as mock_get:
        mock_get.return_value.json.return_value = TestData.colors_1()

        response = api._get_brightness()

        assert response[0] == Response.Success

        for color, value in response[1].items():
            assert value == 0

def test_AquaIPy_get_raw_brightness_all_1000():

    api = TestHelper.get_connected_instance()

    with patch('aquaipy.aquaipy.requests.get') as mock_get:
        mock_get.return_value.json.return_value = TestData.colors_2()

        response = api._get_brightness()

        assert response[0] == Response.Success

        for color, value in response[1].items():
            assert value == 1000

def test_AquaIPy_get_raw_mW_data_hydra26hd():

    api = TestHelper.get_connected_instance()

    with patch('aquaipy.aquaipy.requests.get') as mock_get:
        mock_get.return_value.json.return_value = TestData.power_hydra26hd()

        response, mW_norm, mW_hd, total_max_mW = api._get_mW_limits()

        assert response == Response.Success
        assert total_max_mW == 90000
        
        assert mW_norm["blue"] == 19975
        assert mW_norm["cool_white"] == 23592
        assert mW_norm["violet"] == 7317
        assert mW_norm["green"] == 4190
        assert mW_norm["deep_red"] == 3768
        assert mW_norm["royal"] == 23888
        assert mW_norm["uv"] == 7270

        assert mW_hd["blue"] == 23137
        assert mW_hd["cool_white"] == 32272
        assert mW_hd["violet"] == 8654
        assert mW_hd["green"] == 8769
        assert mW_hd["deep_red"] == 6950
        assert mW_hd["royal"] == 33350
        assert mW_hd["uv"] == 8577


def test_AquaIPy_get_colors():

    api = TestHelper.get_connected_instance()

    with patch.object(api, '_get_brightness') as mock_get:
        
        data = TestData.colors_1()
        del data['response_code']

        mock_get.return_value =  Response.Success, data

        response, colors = api.get_colors()
        assert response == Response.Success
        assert len(colors) == 7


class TestHelper:
    
    @staticmethod
    def get_connected_instance():

        api = AquaIPy()

        with patch('aquaipy.aquaipy.requests.get') as mock_get:
            mock_get.return_value.json.return_value = TestData.identity_1()

            api.connect('test-valid-url')

        return api


