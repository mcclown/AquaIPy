import pytest
from unittest.mock import Mock, patch
import asyncio
import aiohttp
import asynctest
from async_generator import yield_, async_generator

from aquaipy.aquaipy import HDDevice, AquaIPy, Response
from aquaipy.error import ConnError, FirmwareError, MustBeParentError
from aquaipy.test.TestData import TestData


class TestHelper:

    @staticmethod
    def get_hostname(mock_device=None):
        mock_hostname = "localhost"

        if mock_device is None:
            return mock_hostname

        return "{0}:{1}".format(mock_hostname, mock_device.port)

    @staticmethod
    async def async_process_request(mock_device, call_method, expected_request, response_data, request_data = None, expected_method = "GET"):
        task = asyncio.ensure_future(call_method)
        request = await mock_device.receive_request()
        
        # validate request
        assert request.path_qs == expected_request
        assert request.method == expected_method
        if request_data:
            assert (await request.json()) == request_data
         
        mock_device.send_response(request, data=response_data)

        return await task
        
    @staticmethod
    async def async_get_connected_instance(mock_device, identity = TestData.identity_hydra26hd(), power = TestData.power_hydra26hd()):
        api = AquaIPy()
        task = asyncio.ensure_future(api.async_connect(TestHelper.get_hostname(mock_device)))
        
        request = await mock_device.receive_request()
        assert request.path_qs == '/api/identity'
        mock_device.send_response(request, data=identity)
        
        request2 = await mock_device.receive_request()
        assert request2.path_qs == '/api/power'
        mock_device.send_response(request2, data=power)

        await task
        assert api._base_path is not None

        return api


#https://aiohttp.readthedocs.io/en/stable/testing.html#pytest-example
class MockAIDevice(aiohttp.test_utils.RawTestServer):
    def __init__(self, **kwargs):
        super().__init__(self._handle_request, **kwargs)
        self._requests = asyncio.Queue()
        self._responses = {}    #{id(request): Future}

    async def close(self):
        '''Cancel all remaining tasks before closing.'''
        for future in self._responses.values():
            future.cancel()

        await super().close()

    async def _handle_request(self, request):
        '''Push requests to test case and wait until it provides a response'''
        self._responses[id(request)] = response = asyncio.Future()
        self._requests.put_nowait(request)

        try:
            return await response
        finally:
            del self._responses[id(request)]

    async def receive_request(self):
        '''Wait until test server receives a request'''
        return await self._requests.get()

    def send_response(self, request, *args, **kwargs):
        '''Send response from test case to client code'''
        response = aiohttp.web.json_response(*args, **kwargs)
        self._responses[id(request)].set_result(response)


@pytest.fixture
@async_generator
async def device():
    async with MockAIDevice() as device:
        await yield_(device)


@pytest.fixture
@async_generator
async def api(device):
    api = await TestHelper.async_get_connected_instance(device)
    await yield_(api)
    await api._session.close()


@pytest.mark.asyncio
async def test_AquaIPy_init_raises_InvalidURL():
    
    api = AquaIPy()
    with pytest.raises(ConnError):
        await api.async_connect("")
    
    await api._session.close()

@pytest.mark.asyncio
async def test_AquaIPy_init_raises_requests_ConnectionError_bad_hostname():
    
    api = AquaIPy()
    with pytest.raises(ConnError):
        await api.async_connect("invalid-host")

    await api._session.close()

@pytest.mark.asyncio
async def test_AquaIPy_init_raises_requests_MustBeParentError(device):

    api = AquaIPy()
    task = TestHelper.async_process_request(
            device,
            api.async_connect(TestHelper.get_hostname(device)),
            '/api/identity',
            TestData.identity_not_parent())

    with pytest.raises(MustBeParentError):
        await task

    await api._session.close()

@pytest.mark.asyncio
async def test_AquaIPy_init_raises_ConnectionError_server_error(device):
    
    api = AquaIPy()
    task = TestHelper.async_process_request(
            device,
            api.async_connect(TestHelper.get_hostname(device)),
            '/api/identity',
            TestData.server_error())

    with pytest.raises(ConnError):
        await task

    await api._session.close()

@pytest.mark.asyncio
async def test_AquaIPy_init_with_name():

    api = AquaIPy("Test Name")
    assert api.name == "Test Name"

    await api._session.close()

@pytest.mark.asyncio
async def test_AquaIPy_init_success(device, api):

    assert api.mac_addr == "D8976003AAAA"
    assert api.supported_firmware
    assert api.product_type == "Hydra TwentySix"
    assert api.name == None
    assert api.firmware_version == "2.2.0"
    assert api.base_path == "http://{0}/api".format(TestHelper.get_hostname(device))

@pytest.mark.asyncio
async def test_AquaIPy_validate_connection_fail():

    api = AquaIPy()

    with pytest.raises(ConnError):
        await api.async_connect("invalid-host")

    with pytest.raises(ConnError):
        api._validate_connection()

    await api._session.close()
        
@pytest.mark.asyncio
@pytest.mark.parametrize("identity_response, power_response, other_count", [
    (TestData.identity_hydra52hd(), TestData.power_hydra52hd(), 0),
    (TestData.identity_hydra26hd(), TestData.power_hydra26hd(), 0),
    (TestData.identity_primehd(), TestData.power_primehd(), 0),
    (TestData.identity_hydra26hd(), TestData.power_two_hd_devices(), 1),
    (TestData.identity_primehd(), TestData.power_mixed_hd_devices(), 1)
    ])
async def test_AquaIPy_get_devices_success(device, identity_response, power_response, other_count):
    
    api = await TestHelper.async_get_connected_instance(device, identity_response, power_response)

    assert api._primary_device != None
    assert len(api._other_devices) == other_count

    await api._session.close()

@pytest.mark.asyncio
async def test_AquaIPy_get_devices_fail(device, api):

    task = TestHelper.async_process_request(
            device,
            api._async_get_devices(),
            '/api/power',
            TestData.server_error())

    with pytest.raises(ConnError):
        await task

@pytest.mark.asyncio
async def test_AquaIPy_firmware_error(device):

    api = AquaIPy()
    task = TestHelper.async_process_request(
            device, 
            api.async_connect(TestHelper.get_hostname(device)), 
            '/api/identity', 
            TestData.identity_hydra26hd_unsupported_firmware())

    with pytest.raises(FirmwareError):
        await task

    await api._session.close()

@pytest.mark.asyncio
async def test_AquaIPy_get_schedule_state_enabled(device, api):

    response = await TestHelper.async_process_request(
            device,
            api.async_get_schedule_state(),
            '/api/schedule/enable',
            TestData.schedule_enabled())
    
    assert response == True

@pytest.mark.asyncio
async def test_AquaIPy_get_schedule_state_disabled(device, api):

    response = await TestHelper.async_process_request(
            device, 
            api.async_get_schedule_state(), 
            '/api/schedule/enable', 
            TestData.schedule_disabled())

    assert response == False

@pytest.mark.asyncio
async def test_AquaIPy_get_schedule_state_error(device, api):

    response = await TestHelper.async_process_request(
            device, 
            api.async_get_schedule_state(), 
            '/api/schedule/enable', 
            TestData.server_error())

    assert response == None

@pytest.mark.asyncio
async def test_AquaIPy_get_schedule_state_error_unexpected_response(device, api):

    response = await TestHelper.async_process_request(
            device, 
            api.async_get_schedule_state(), 
            '/api/schedule/enable', 
            None)

    assert response == None

@pytest.mark.asyncio
async def test_AquaIPy_get_raw_brightness_all_0(device, api):

    response = await TestHelper.async_process_request(
            device, 
            api._async_get_brightness(), 
            '/api/colors', 
            TestData.colors_1())
    
    assert response[0] == Response.Success

    for color, value in response[1].items():
        assert value == 0

@pytest.mark.asyncio
async def test_AquaIPy_get_raw_brightness_all_1000(device, api):

    response = await TestHelper.async_process_request(
            device, 
            api._async_get_brightness(), 
            '/api/colors', 
            TestData.colors_2())
    
    assert response[0] == Response.Success

    for color, value in response[1].items():
        assert value == 1000

@pytest.mark.asyncio
async def test_AquaIPy_get_raw_brightness_error(device, api):

    response = await TestHelper.async_process_request(
            device,
            api._async_get_brightness(),
            '/api/colors',
            TestData.server_error())

    assert response == (Response.Error, None)

@pytest.mark.asyncio
async def test_AquaIPy_get_colors(api):

    with asynctest.patch.object(api, '_async_get_brightness') as mock_get:
        
        data = TestData.colors_1()
        del data['response_code']

        mock_get.return_value =  Response.Success, data

        colors = await api.async_get_colors()
        assert len(colors) == 7

@pytest.mark.asyncio
async def test_AquaIPy_get_colors_error(api):

    with asynctest.patch.object(api, '_async_get_brightness') as mock_get:

        mock_get.return_value = (Response.Error, None)
        response = await api.async_get_colors()

        assert response == None

@pytest.mark.asyncio
async def test_AquaIPy_get_color_brightness_error(api):

    with asynctest.patch.object(api, '_async_get_brightness') as mock_getb:

        data = TestData.colors_1()
        del data['response_code']
        mock_getb.return_value = Response.Error, None


        colors = await api.async_get_colors_brightness()
        assert colors == None

@pytest.mark.asyncio
async def test_AquaIPy_get_color_brightness_all_0(api):

    with asynctest.patch.object(api, '_async_get_brightness') as mock_getb:

            data = TestData.colors_1()
            del data['response_code']
            mock_getb.return_value = Response.Success, data


            colors = await api.async_get_colors_brightness()
            mock_getb.assert_called_once_with()
            assert len(colors) == 7

            for color, value in colors.items():
                assert value == 0

@pytest.mark.asyncio
async def test_AquaIPy_get_color_brightness_all_100(api):

    with asynctest.patch.object(api, '_async_get_brightness') as mock_getb:
            data = TestData.colors_2()
            del data['response_code']
            mock_getb.return_value = Response.Success, data

            colors = await api.async_get_colors_brightness()
            mock_getb.assert_called_once_with()
            assert len(colors) == 7

            for color, value in colors.items():
                assert value == 100

@pytest.mark.asyncio
async def test_AquaIPy_get_color_brightness_hd_values(api):

    with asynctest.patch.object(api, '_async_get_brightness') as mock_getb:

        data = TestData.colors_3()
        del data['response_code']
        mock_getb.return_value = Response.Success, data


        colors = await api.async_get_colors_brightness()
        mock_getb.assert_called_once_with()
        assert len(colors) == 7

        for color, value in colors.items():

            if color == 'uv':
                assert value == 42.4
            elif color == 'violet':
                assert value == 104.78739920732541
            elif color == 'royal':
                assert value == 117.23028298727394
            else:
                assert value == 0

@pytest.mark.asyncio
async def test_AquaIPy_set_brightnessde(device, api):
    
        data = TestData.colors_1()
        del data['response_code']

        response = await TestHelper.async_process_request(
                device,
                api._async_set_brightness(data),
                '/api/colors',
                TestData.server_success(),
                data,
                "POST")

        assert response == Response.Success

@pytest.mark.asyncio
async def test_AquaIPy_set_brightness_error(device, api):

    data = TestData.colors_1()
    del data['response_code']

    response = await TestHelper.async_process_request(
            device,
            api._async_set_brightness(data),
            '/api/colors',
            TestData.server_error(),
            data,
            "POST")

    assert response == Response.Error

@pytest.mark.asyncio
async def test_AquaIPy_set_schedule_enabled(device, api):

    response = await TestHelper.async_process_request(
            device,
            api.async_set_schedule_state(True),
            '/api/schedule/enable',
            TestData.server_success(),
            {"enable": True},
            "PUT")

    assert response == Response.Success

@pytest.mark.asyncio
async def test_AquaIPy_set_schedule_disabled(device, api):
    
    response = await TestHelper.async_process_request(
            device,
            api.async_set_schedule_state(False),
            '/api/schedule/enable',
            TestData.server_success(),
            {"enable": False},
            "PUT")

    assert response == Response.Success

@pytest.mark.asyncio
async def test_AquaIPy_set_schedule_error(device, api):

    response = await TestHelper.async_process_request(
            device,
            api.async_set_schedule_state(False),
            '/api/schedule/enable',
            TestData.server_error(),
            {"enable": False},
            "PUT")

    assert response == Response.Error

@pytest.mark.asyncio
async def test_AquaIPy_set_schedule_error_unexpected_response(device, api):

    response = await TestHelper.async_process_request(
            device,
            api.async_set_schedule_state(False),
            '/api/schedule/enable',
            None,
            {"enable": False},
            "PUT")

    assert response == Response.Error

@pytest.mark.asyncio
async def test_AquaIPy_patch_color_brightness_all_0(api):

    with asynctest.patch.object(api, 'async_get_colors_brightness') as mock_get:
        with asynctest.patch.object(api, 'async_set_colors_brightness') as mock_set:
            
            data = TestData.colors_1()
            del data['response_code']
            mock_get.return_value = data
            mock_set.return_value = Response.Success

            response = await api.async_patch_colors_brightness(TestData.set_colors_1())

            assert response == Response.Success
            mock_set.assert_called_once_with(data)

@pytest.mark.asyncio
async def test_AquaIPy_patch_color_brightness_all_100(api):

    with asynctest.patch.object(api, 'async_set_colors_brightness') as mock_set:
        with asynctest.patch.object(api, 'async_get_colors_brightness') as mock_get:

            data = TestData.colors_1()
            del data['response_code']
            mock_get.return_value = data
            mock_set.return_value = Response.Success

            response = await api.async_patch_colors_brightness(TestData.set_colors_2())

            result = TestData.set_colors_2()

            assert response == Response.Success
            mock_set.assert_called_once_with(result)

@pytest.mark.asyncio
async def test_AquaIPy_patch_color_brightness_hd_values(api):

    with asynctest.patch.object(api, 'async_set_colors_brightness') as mock_set:
        with asynctest.patch.object(api, 'async_get_colors_brightness') as mock_get:

            data = TestData.colors_1()
            del data['response_code']
            mock_get.return_value = data
            mock_set.return_value = Response.Success

            response = await api.async_patch_colors_brightness(TestData.set_colors_3())

            result = TestData.set_colors_3()

            assert response == Response.Success
            mock_set.assert_called_once_with(result)

@pytest.mark.asyncio
async def test_AquaIPy_patch_color_brightness_invalid_data(api):

    data = TestData.colors_1()
    del data['response_code']

    response = await api.async_patch_colors_brightness({})
    assert response == Response.InvalidData

@pytest.mark.asyncio
async def test_AquaIPy_patch_color_error_response(api):

    with asynctest.patch.object(api, 'async_get_colors_brightness') as mock_get:

        mock_get.return_value = None

        result = await api.async_patch_colors_brightness(TestData.set_colors_3())

        assert result == Response.Error

@pytest.mark.asyncio
async def test_AquaIPy_update_color_brightness(api):

    with asynctest.patch.object(api, 'async_set_colors_brightness') as mock_set:
        with asynctest.patch.object(api, 'async_get_colors_brightness') as mock_get:

            data = TestData.colors_1()
            del data['response_code']
            mock_get.return_value = data
            mock_set.return_value = Response.Success

            response = await api.async_update_color_brightness('blue', 20)

            result = TestData.set_colors_1()
            result['blue'] = 20

            assert response == Response.Success
            mock_set.assert_called_once_with(result)

@pytest.mark.asyncio
async def test_AquaIPy_update_color_brightness_too_high(api):

    with asynctest.patch.object(api, 'async_set_colors_brightness') as mock_set:
        with asynctest.patch.object(api, 'async_get_colors_brightness') as mock_get:

            data = TestData.colors_1()
            del data['response_code']
            mock_get.return_value = data
            mock_set.return_value = Response.Success

            response = await api.async_update_color_brightness('blue', 110)

            result = TestData.set_colors_1()
            result['blue'] = 110

            assert response == Response.Success
            mock_set.assert_called_once_with(result)

@pytest.mark.asyncio
async def test_AquaIPy_update_color_brightness_too_low(api):

    with asynctest.patch.object(api, 'async_set_colors_brightness') as mock_set:
        with asynctest.patch.object(api, 'async_get_colors_brightness') as mock_get:

            data = TestData.colors_1()
            del data['response_code']
            mock_get.return_value = data
            mock_set.return_value = Response.Success

            response = await api.async_update_color_brightness('blue', -10)

            result = TestData.set_colors_1()
            result['blue'] = -10

            assert response == Response.Success
            mock_set.assert_called_once_with(result)

@pytest.mark.asyncio
async def test_AquaIPy_update_color_brightness_invalid_data(api):

    response = await api.async_update_color_brightness("", 0.0)
    assert response == Response.InvalidData

@pytest.mark.asyncio
async def test_AquaIPy_update_color_error_response(api):

    with asynctest.patch.object(api, 'async_get_colors_brightness') as mock_get:

        mock_get.return_value = None 

        result = await api.async_update_color_brightness("deep_red", 10)

        assert result == Response.Error

@pytest.mark.asyncio
async def test_AquaIPy_update_color_brightness_no_action_required(api):

    response = await api.async_update_color_brightness("deep_red", 0.0)
    assert response == Response.Success

@pytest.mark.asyncio
async def test_AquaIPy_set_color_brightness_error(api):

    with asynctest.patch.object(api, 'async_get_colors') as mock_get_colors:
        with asynctest.patch.object(api, '_async_set_brightness') as mock_set:

            mock_get_colors.return_value = TestData.get_colors()
            mock_set.return_value = Response.Success

            response = await api.async_set_colors_brightness({})
            assert response == Response.AllColorsMustBeSpecified

@pytest.mark.asyncio
@pytest.mark.parametrize("identity_response, power_response, result", [
    (TestData.identity_hydra26hd(), TestData.power_hydra26hd(), TestData.set_result_colors_3_hydra26hd()),
    (TestData.identity_primehd(), TestData.power_primehd(), TestData.set_result_colors_3_primehd()),
    (TestData.identity_hydra26hd(), TestData.power_two_hd_devices(), TestData.set_result_colors_3_hydra26hd()),
    (TestData.identity_primehd(), TestData.power_mixed_hd_devices(), TestData.set_result_colors_3_primehd())
    ])
async def test_AquaIPy_set_color_brightness_hd(device, identity_response, power_response, result):

    api = await TestHelper.async_get_connected_instance(device, identity_response, power_response)

    with asynctest.patch.object(api, 'async_get_colors') as mock_get_colors:
        with asynctest.patch.object(api, '_async_set_brightness') as mock_set:

            mock_get_colors.return_value = TestData.get_colors()
            mock_set.return_value = Response.Success

            await api.async_set_colors_brightness(TestData.set_colors_3())

            mock_set.assert_called_once_with(result)

    await api._session.close()

@pytest.mark.asyncio
@pytest.mark.parametrize("set_colors_max_hd, result_colors_max_hd, identity_response, power_response", [
    (TestData.set_colors_max_hd_hydra52hd(), TestData.set_result_colors_max_hd_hydra52hd(), TestData.identity_hydra52hd(), TestData.power_hydra52hd()),
    (TestData.set_colors_max_hd_hydra26hd(), TestData.set_result_colors_max_hd_hydra26hd(), TestData.identity_hydra26hd(), TestData.power_hydra26hd()),
    (TestData.set_colors_max_hd_primehd(), TestData.set_result_colors_max_hd_primehd(), TestData.identity_primehd(), TestData.power_primehd())
    ])
async def test_AquaIPy_set_color_brightness_max_hd(device, set_colors_max_hd, result_colors_max_hd, identity_response, power_response):

    api = await TestHelper.async_get_connected_instance(device, identity_response, power_response)

    with asynctest.patch.object(api, 'async_get_colors') as mock_get_colors:
        with asynctest.patch.object(api, '_async_set_brightness') as mock_set:

            mock_get_colors.return_value = TestData.get_colors()
            mock_set.return_value = Response.Success

            response = await api.async_set_colors_brightness(set_colors_max_hd)

            mock_set.assert_called_once_with(result_colors_max_hd)
            assert response == Response.Success

    await api._session.close()

@pytest.mark.asyncio
@pytest.mark.parametrize("identity_response, power_response, set_colors", [
    (TestData.identity_hydra26hd(), TestData.power_hydra26hd(), TestData.set_colors_hd_exceeded_hydra26hd()),
    (TestData.identity_primehd(), TestData.power_primehd(), TestData.set_colors_hd_exceeded_primehd()),
    (TestData.identity_hydra26hd(), TestData.power_two_hd_devices(), TestData.set_colors_max_hd_primehd()),
    (TestData.identity_primehd(), TestData.power_mixed_hd_devices(), TestData.set_colors_hd_exceeded_mixed())
    ])
async def test_AquaIPy_set_color_brightness_hd_exceeded(device, identity_response, power_response, set_colors):

    api = await TestHelper.async_get_connected_instance(device, identity_response, power_response)

    with asynctest.patch.object(api, 'async_get_colors') as mock_get_colors:
        with asynctest.patch.object(api, '_async_set_brightness') as mock_set:

            mock_get_colors.return_value = TestData.get_colors()

            result = await api.async_set_colors_brightness(set_colors)

            mock_set.assert_not_called()
            assert result == Response.PowerLimitExceeded

    await api._session.close()


""" These aren't async tests but they conflict with the fixtures used for the
    synchronous tests, so I'm adding them here instead.
"""


def test_init_with_session():

    session = aiohttp.ClientSession()

    api = AquaIPy(session=session)

    api.close()


def test_init_with_no_asyncio_loop_running():

    #Close current loop 
    loop = asyncio.get_event_loop()
    loop.stop()
    pending_tasks = asyncio.Task.all_tasks()
    loop.run_until_complete(asyncio.gather(*pending_tasks))
    loop.close()

    api = AquaIPy()

    api.close()

    #Add new loop again
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)


def test_init_with_specified_loop():

    loop = asyncio.get_event_loop()

    api = AquaIPy(loop=loop)


@patch("aquaipy.aquaipy.asyncio.get_event_loop", side_effect=RuntimeError("Testing this exception handling."))
def test_init_get_event_loop_error(mock_get):

    with pytest.raises(RuntimeError):
        api = AquaIPy()


