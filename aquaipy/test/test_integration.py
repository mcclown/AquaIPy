import pytest
import time
from unittest.mock import Mock, patch

import requests
from aquaipy.aquaipy import HDDevice, AquaIPy, Response
from aquaipy.error import ConnError, FirmwareError, MustBeParentError
from aquaipy.test import ENDPOINT_CONFIG_NAME

ENDPOINT = pytest.config.getini(ENDPOINT_CONFIG_NAME)
endpoint_defined = pytest.mark.skipif(ENDPOINT == '', reason = "No endpoint defined for integration tests")


@pytest.fixture(scope="module")
def ai_instance():

    ai_instance = AquaIPy()
    ai_instance.connect(ENDPOINT)

    #Store current light state
    sched_state = ai_instance.get_schedule_state()
    color_state = ai_instance.get_colors_brightness()

    yield ai_instance

    #Restore light state
    ai_instance.set_schedule_state(sched_state)
    ai_instance.set_colors_brightness(color_state)

    ai_instance.close()


@endpoint_defined
@pytest.mark.parametrize("percent", [0, 50, 100])
def test_set_colors(ai_instance, percent):

    ai = ai_instance

    colors = ai.get_colors_brightness()

    assert colors != None

    for color, value in colors.items():
        colors[color] = percent

    resp = ai.set_colors_brightness(colors)

    assert resp == Response.Success

    #Validation
    new_colors = ai.get_colors_brightness()

    for color, value in new_colors.items():
        assert value == percent, "{0} is not {1}".format(color, percent)


@endpoint_defined
@pytest.mark.parametrize("base_percent, patch_percent, patch_target", [(10, 50, 'deep_red'), (20, 80, 'blue'), (50, 100, 'cool_white')])
def test_patch_color(ai_instance, base_percent, patch_percent, patch_target):

    ai = ai_instance

    colors = ai.get_colors_brightness()

    for color, value in colors.items():
        colors[color] = base_percent

    resp = ai.set_colors_brightness(colors)
    assert resp == Response.Success

    resp = ai.patch_colors_brightness({patch_target: patch_percent})
    assert resp == Response.Success

    #Validation
    new_colors = ai.get_colors_brightness()

    for color, value in new_colors.items():

        if color == patch_target:
            assert value == patch_percent
        else:
            assert value == base_percent


@endpoint_defined
@pytest.mark.parametrize("base_percent, update_percent, update_target", [(10, 10, 'deep_red'), (20, 30, 'blue'), (50, -10, 'cool_white')])
def test_update_color(ai_instance, base_percent, update_percent, update_target):

    ai = ai_instance

    colors = ai.get_colors_brightness()

    for color, value in colors.items():
        colors[color] = base_percent

    resp = ai.set_colors_brightness(colors)
    assert resp == Response.Success

    resp = ai.update_color_brightness(update_target, update_percent)
    assert resp == Response.Success

    #Validation
    new_colors = ai.get_colors_brightness()

    for color, value in new_colors.items():

        if color == update_target:
            assert value == base_percent + update_percent
        else:
            assert value == base_percent

