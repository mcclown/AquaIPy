import pytest
from unittest.mock import Mock, patch
import decimal

from aquaipy.aquaipy import HDDevice, AquaIPy, Response
from aquaipy.error import ConnError, FirmwareError, MustBeParentError
from aquaipy.test.TestData import TestData


@pytest.mark.parametrize("power_response, primary_mac, max_mw", [
    (TestData.power_hydra52hd(), TestData.primary_mac_hydra52hd(), TestData.power_hydra52hd_max()),
    (TestData.power_hydra26hd(), TestData.primary_mac_hydra26hd(), TestData.power_hydra26hd_max()),
    (TestData.power_primehd(), TestData.primary_mac_primehd(), TestData.power_primehd_max())
    ])
def test_HDDevice_init(power_response, primary_mac, max_mw):

    device = HDDevice(power_response["devices"][0], primary_mac)

    assert device.is_primary
    assert device.max_mw == max_mw


@pytest.mark.parametrize("power_response, primary_mac, percentage, result_intensities", [
    (TestData.power_hydra26hd(), TestData.primary_mac_hydra26hd(), 0, TestData.result_intensities_0p()),
    (TestData.power_primehd(), TestData.primary_mac_primehd(), 0, TestData.result_intensities_0p()),
    (TestData.power_hydra26hd(), TestData.primary_mac_hydra26hd(), 33.333, TestData.result_intensities_33_333p()),
    (TestData.power_primehd(), TestData.primary_mac_primehd(), 33.333, TestData.result_intensities_33_333p()),
    (TestData.power_hydra26hd(), TestData.primary_mac_hydra26hd(), 100, TestData.result_intensities_100p()),
    (TestData.power_primehd(), TestData.primary_mac_primehd(), 100, TestData.result_intensities_100p()),
    (TestData.power_hydra26hd(), TestData.primary_mac_hydra26hd(), 105, TestData.result_intensities_105p_hydra26hd()),
    (TestData.power_primehd(), TestData.primary_mac_primehd(), 105, TestData.result_intensities_105p_primehd()),
    (TestData.power_hydra26hd(), TestData.primary_mac_hydra26hd(), 107.5893, TestData.result_intensities_107_5893p_hydra26hd()),
    (TestData.power_primehd(), TestData.primary_mac_primehd(), 107.5893, TestData.result_intensities_107_5893p_primehd()),
    (TestData.power_hydra26hd(), TestData.primary_mac_hydra26hd(), 110, TestData.result_intensities_110p_hydra26hd()),
    (TestData.power_primehd(), TestData.primary_mac_primehd(), 110, TestData.result_intensities_110p_primehd())
    ])
def test_HDDevice_convert_to_intensity(power_response, primary_mac, percentage, result_intensities):

    device = HDDevice(power_response["devices"][0], primary_mac)

    for color in TestData.get_colors():

        assert result_intensities[color] == device.convert_to_intensity(color, percentage)


@pytest.mark.parametrize("percentage", [-10, 300]) 
def test_HDDevice_convert_to_intensity_ValueError(percentage):

    device = HDDevice(TestData.power_hydra26hd()["devices"][0], TestData.primary_mac_hydra26hd())

    with pytest.raises(ValueError):
        device.convert_to_intensity("uv", percentage)


@pytest.mark.parametrize("power_response, primary_mac, resulting_percentage, input_intensities", [
    (TestData.power_hydra26hd(), TestData.primary_mac_hydra26hd(), 0, TestData.result_intensities_0p()),
    (TestData.power_primehd(), TestData.primary_mac_primehd(), 0, TestData.result_intensities_0p()),
    (TestData.power_hydra26hd(), TestData.primary_mac_hydra26hd(), 100, TestData.result_intensities_100p()),
    (TestData.power_primehd(), TestData.primary_mac_primehd(), 100, TestData.result_intensities_100p()),
    (TestData.power_hydra26hd(), TestData.primary_mac_hydra26hd(), 105, TestData.result_intensities_105p_hydra26hd()),
    (TestData.power_primehd(), TestData.primary_mac_primehd(), 105, TestData.result_intensities_105p_primehd()),
    (TestData.power_hydra26hd(), TestData.primary_mac_hydra26hd(), 110, TestData.result_intensities_110p_hydra26hd()),
    (TestData.power_primehd(), TestData.primary_mac_primehd(), 110, TestData.result_intensities_110p_primehd())
    ])
def test_HDDevice_convert_to_percentage(power_response, primary_mac, resulting_percentage, input_intensities):

    device = HDDevice(power_response["devices"][0], primary_mac)

    for color in TestData.get_colors():

        assert resulting_percentage == round(device.convert_to_percentage(color, input_intensities[color]))


@pytest.mark.parametrize("intensity", [-10, 2010]) 
def test_HDDevice_convert_to_percentage_ValueError(intensity):

    device = HDDevice(TestData.power_hydra26hd()["devices"][0], TestData.primary_mac_hydra26hd())

    with pytest.raises(ValueError):
        device.convert_to_percentage("uv", intensity)


@pytest.mark.parametrize("power_response, primary_mac, intensity, result_mw", [
    (TestData.power_hydra26hd(), TestData.primary_mac_hydra26hd(), 0, TestData.result_mw_hydra26hd_0()),
    (TestData.power_primehd(), TestData.primary_mac_primehd(), 0, TestData.result_mw_primehd_0()),
    (TestData.power_hydra26hd(), TestData.primary_mac_hydra26hd(), 500, TestData.result_mw_hydra26hd_500()),
    (TestData.power_primehd(), TestData.primary_mac_primehd(), 500, TestData.result_mw_primehd_500()),
    (TestData.power_hydra26hd(), TestData.primary_mac_hydra26hd(), 1000, TestData.result_mw_hydra26hd_1000()),
    (TestData.power_primehd(), TestData.primary_mac_primehd(), 1000, TestData.result_mw_primehd_1000()),
    (TestData.power_hydra26hd(), TestData.primary_mac_hydra26hd(), 1500, TestData.result_mw_hydra26hd_1500()),
    (TestData.power_primehd(), TestData.primary_mac_primehd(), 1500, TestData.result_mw_primehd_1500()),
    (TestData.power_hydra26hd(), TestData.primary_mac_hydra26hd(), 2000, TestData.result_mw_hydra26hd_2000()),
    (TestData.power_primehd(), TestData.primary_mac_primehd(), 2000, TestData.result_mw_primehd_2000()),
    ])
def test_HDDevice_convert_to_mw(power_response, primary_mac, intensity, result_mw):

    device = HDDevice(power_response["devices"][0], primary_mac)

    for color in TestData.get_colors():

        assert result_mw[color]  == device.convert_to_mw(color, intensity)


@pytest.mark.parametrize("intensity", [-10, 2010]) 
def test_HDDevice_convert_to_mw_ValueError(intensity):

    device = HDDevice(TestData.power_hydra26hd()["devices"][0], TestData.primary_mac_hydra26hd())

    with pytest.raises(ValueError):
        device.convert_to_mw("uv", intensity)


