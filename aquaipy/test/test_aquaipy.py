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
    assert api.firmware_version == "2.0.0"
    assert api.base_path == 'http://' + TestHelper.mock_hostname + '/api'


@patch('aquaipy.aquaipy.requests.get')
def test_AquaIPy_firmware_error(mock_get):

    mock_get.return_value.json.return_value = TestData.identity_2()

    api = AquaIPy()
    with pytest.raises(NotImplementedError):
        api.connect(TestHelper.mock_hostname)


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

def test_AquaIPy_get_schedule_state_error():

    api = TestHelper.get_connected_instance()

    with patch('aquaipy.aquaipy.requests.get') as mock_get:
        mock_get.return_value.json.return_value = TestData.server_error

        assert api.get_schedule_state() == None


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


def test_AquaIPy_get_raw_brightness_error():

    api = TestHelper.get_connected_instance()

    with patch('aquaipy.aquaipy.requests.get') as mock_get:
        mock_get.return_value.json.return_value = TestData.server_error()

        response = api._get_brightness()

        assert response == (Response.Error, None)


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

def test_AquaIPy_get_raw_mW_data_error():

    api = TestHelper.get_connected_instance()

    with patch('aquaipy.aquaipy.requests.get') as mock_get:

        mock_get.return_value.json.return_value = TestData.server_error()

        response = api._get_mW_limits()

        assert response == (Response.Error, None, None, None)


def test_AquaIPy_get_colors():

    api = TestHelper.get_connected_instance()

    with patch.object(api, '_get_brightness') as mock_get:
        
        data = TestData.colors_1()
        del data['response_code']

        mock_get.return_value =  Response.Success, data

        response, colors = api.get_colors()
        assert response == Response.Success
        assert len(colors) == 7

def test_AquaIPy_get_colors_error():

    api = TestHelper.get_connected_instance()

    with patch.object(api, '_get_brightness') as mock_get:

        mock_get.return_value = (Response.Error, None)

        response = api.get_colors()

        assert response == (Response.Error, None)

def test_AquaIPy_get_color_brightness_all_0():

    api = TestHelper.get_connected_instance()

    with patch.object(api, '_get_brightness') as mock_getb:
        with patch.object(api, '_get_mW_limits') as mock_getl:

            data = TestData.colors_1()
            del data['response_code']
            mock_getb.return_value = Response.Success, data

            mock_getl.return_value = Response.Success, TestData.power_hydra26hd_norm, TestData.power_hydra26hd_hd, TestData.power_hydra26hd_max

            response, colors = api.get_color_brightness()
            assert response == Response.Success
            mock_getb.assert_called_once_with()
            mock_getl.assert_not_called()
            assert len(colors) == 7

            for color, value in colors.items():
                assert value == 0

def test_AquaIPy_get_color_brightness_all_100():

    api = TestHelper.get_connected_instance()

    with patch.object(api, '_get_brightness') as mock_getb:
        with patch.object(api, '_get_mW_limits') as mock_getl:

            data = TestData.colors_2()
            del data['response_code']
            mock_getb.return_value = Response.Success, data

            mock_getl.return_value = Response.Success, TestData.power_hydra26hd_norm, TestData.power_hydra26hd_hd, TestData.power_hydra26hd_max

            response, colors = api.get_color_brightness()
            assert response == Response.Success
            mock_getb.assert_called_once_with()
            mock_getl.assert_not_called()
            assert len(colors) == 7

            for color, value in colors.items():
                assert value == 100

def test_AquaIPy_get_color_brightness_hd_values():

    api = TestHelper.get_connected_instance()

    with patch.object(api, '_get_brightness') as mock_getb:
        with patch.object(api, '_get_mW_limits') as mock_getl:

            data = TestData.colors_3()
            del data['response_code']
            mock_getb.return_value = Response.Success, data

            mock_getl.return_value = Response.Success, TestData.power_hydra26hd_norm(), TestData.power_hydra26hd_hd(), TestData.power_hydra26hd_max()

            response, colors = api.get_color_brightness()
            assert response == Response.Success
            mock_getb.assert_called_once_with()
            mock_getl.assert_called_once_with()
            assert len(colors) == 7

            for color, value in colors.items():

                if color == 'uv':
                    assert value == 42
                elif color == 'violet':
                    assert value == 105
                elif color == 'royal':
                    assert value == 117
                else:
                    assert value == 0


def test_AquaIPy_set_brightness():
    
    api = TestHelper.get_connected_instance()

    with patch('aquaipy.aquaipy.requests.post')  as mock_post:
        
        mock_post.return_value.json.return_value = TestData.server_success()

        data = TestData.colors_1()
        del data['response_code']

        response = api._set_brightness(data)

        assert response == Response.Success
        mock_post.assert_called_once_with(api.base_path + '/colors', json = data)


def test_AquaIPy_set_schedule_enabled():

    api = TestHelper.get_connected_instance()

    with patch('aquaipy.aquaipy.requests.put') as mock_put:

        mock_put.return_value.json.return_value = TestData.server_success()

        response = api.set_schedule_state(True)

        assert response == Response.Success
        mock_put.assert_called_once_with(api.base_path + '/schedule/enable', data='{"enable": true}')


def test_AquaIPy_set_schedule_disabled():

    api = TestHelper.get_connected_instance()

    with patch('aquaipy.aquaipy.requests.put') as mock_put:

        mock_put.return_value.json.return_value = TestData.server_success()

        response = api.set_schedule_state(False)

        assert response == Response.Success
        mock_put.assert_called_once_with(api.base_path + '/schedule/enable', data='{"enable": false}')


def test_AquaIPy_patch_color_brightness_all_0():

    api = TestHelper.get_connected_instance()

    with patch.object(api, 'set_color_brightness') as mock_set:
        with patch.object(api, 'get_color_brightness') as mock_get:

            data = TestData.colors_1()
            del data['response_code']
            mock_get.return_value = Response.Success, data
            mock_set.return_value = Response.Success

            response = api.patch_color_brightness(TestData.set_colors_1())

            assert response == Response.Success
            mock_set.assert_called_once_with(data)

def test_AquaIPy_patch_color_brightness_all_100():

    api = TestHelper.get_connected_instance()

    with patch.object(api, 'set_color_brightness') as mock_set:
        with patch.object(api, 'get_color_brightness') as mock_get:

            data = TestData.colors_1()
            del data['response_code']
            mock_get.return_value = Response.Success, data
            mock_set.return_value = Response.Success

            response = api.patch_color_brightness(TestData.set_colors_2())

            result = TestData.set_colors_2()

            assert response == Response.Success
            mock_set.assert_called_once_with(result)


def test_AquaIPy_patch_color_brightness_hd_values():

    api = TestHelper.get_connected_instance()

    with patch.object(api, 'set_color_brightness') as mock_set:
        with patch.object(api, 'get_color_brightness') as mock_get:

            data = TestData.colors_1()
            del data['response_code']
            mock_get.return_value = Response.Success, data
            mock_set.return_value = Response.Success

            response = api.patch_color_brightness(TestData.set_colors_3())

            result = TestData.set_colors_3()

            assert response == Response.Success
            mock_set.assert_called_once_with(result)


def test_AquaIPy_update_color_brightness():

    api = TestHelper.get_connected_instance()

    with patch.object(api, 'set_color_brightness') as mock_set:
        with patch.object(api, 'get_color_brightness') as mock_get:

            data = TestData.colors_1()
            del data['response_code']
            mock_get.return_value = Response.Success, data
            mock_set.return_value = Response.Success

            response = api.update_color_brightness({'blue': 20})

            result = TestData.set_colors_1()
            result['blue'] = 20

            assert response == Response.Success
            mock_set.assert_called_once_with(result)


def test_AquaIPy_update_color_brightness_too_high():

    api = TestHelper.get_connected_instance()

    with patch.object(api, 'set_color_brightness') as mock_set:
        with patch.object(api, 'get_color_brightness') as mock_get:

            data = TestData.colors_1()
            del data['response_code']
            mock_get.return_value = Response.Success, data
            mock_set.return_value = Response.Success

            response = api.update_color_brightness({'blue': 110})

            result = TestData.set_colors_1()
            result['blue'] = 110

            assert response == Response.Success
            mock_set.assert_called_once_with(result)


def test_AquaIPy_update_color_brightness_too_low():

    api = TestHelper.get_connected_instance()

    with patch.object(api, 'set_color_brightness') as mock_set:
        with patch.object(api, 'get_color_brightness') as mock_get:

            data = TestData.colors_1()
            del data['response_code']
            mock_get.return_value = Response.Success, data
            mock_set.return_value = Response.Success

            response = api.update_color_brightness({'blue': -10})

            result = TestData.set_colors_1()
            result['blue'] = -10

            assert response == Response.Success
            mock_set.assert_called_once_with(result)

def test_AquaIPy_set_color_brightness_hd():

    api = TestHelper.get_connected_instance()

    with patch.object(api, 'get_colors') as mock_get_colors:
        with patch.object(api, '_get_mW_limits') as mock_get_limits:
            with patch.object(api, '_set_brightness') as mock_set:

                mock_get_colors.return_value = TestData.get_colors()
                mock_get_limits.return_value = Response.Success, TestData.power_hydra26hd_norm(), TestData.power_hydra26hd_hd(), TestData.power_hydra26hd_max()
                mock_set.return_value = Response.Success

                api.set_color_brightness(TestData.set_colors_3())

                mock_set.assert_called_once_with(TestData.set_result_colors_3())



class TestHelper:

    mock_hostname = 'valid-hostname'
    
    @staticmethod
    def get_connected_instance():

        api = AquaIPy()

        with patch('aquaipy.aquaipy.requests.get') as mock_get:
            mock_get.return_value.json.return_value = TestData.identity_1()

            api.connect(TestHelper.mock_hostname)

        return api



