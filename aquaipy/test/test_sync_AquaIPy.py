from multiprocessing import Process
import socket
import pytest
from unittest.mock import Mock, patch
import asyncio
import aiohttp
from aiohttp import web

from aquaipy.aquaipy import HDDevice, AquaIPy, Response
from aquaipy.error import ConnError, FirmwareError, MustBeParentError
from aquaipy.test.TestData import TestData


def get_hostname():
    return "localhost"


@pytest.fixture(scope='module')
def bound_socket():
    # Bind to random port, then start server on that port
    sock = socket.socket()
    sock.bind((get_hostname(), 0))
    sock.listen(128) # Magic number is default used by aiohttp.
    return sock


@pytest.fixture(scope='module')
def server_process(bound_socket):

    app = aiohttp.web.Application()
    
    def identity_handler(request):
        return web.json_response(data=TestData.identity_hydra26hd())

    def power_handler(request):
        return web.json_response(data=TestData.power_hydra26hd())

    def schedule_state_handler(request):
        return web.json_response(data=TestData.schedule_enabled())

    def colors_handler(request):
        return web.json_response(data=TestData.colors_1())

    app.router.add_route('get', '/api/identity', identity_handler)
    app.router.add_route('get', '/api/power', power_handler)
    app.router.add_route('get', '/api/schedule/enable', schedule_state_handler)
    app.router.add_route('get', '/api/colors', colors_handler)

    def run_server():
        aiohttp.web.run_app(app, handle_signals=True, sock=bound_socket)
    
    p = Process(target=run_server)
    p.start()

    yield p

    p.terminate()
    p.join()


@pytest.fixture
def ai_instance(bound_socket, server_process):

    host = get_hostname()
    _, port = bound_socket.getsockname()

    api = AquaIPy()
       
    # The app runner/process takes a while to startup, so wait for it.
    for i in range(0, 10):

        try:
            api.connect("{0}:{1}".format(host, port))
        except Exception as e:
            assertIsInstance(e, ConnError)

    api._validate_connection()

    return api
 

def test_sync_connect_and_close(ai_instance):

    ai_instance._validate_connection()
    ai_instance.close()


def test_sync_get_schedule_state(ai_instance):

    assert ai_instance.get_schedule_state()
    ai_instance.close()


def test_sync_get_colors(ai_instance):

    expected_colors = TestData.get_colors()
    returned_colors = ai_instance.get_colors()

    for color in expected_colors:
        assert returned_colors.index(color) >= 0

    ai_instance.close()



