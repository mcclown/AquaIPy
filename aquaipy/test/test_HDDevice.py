import pytest
from unittest.mock import Mock, patch

from aquaipy import AquaIPy, Response 
from aquaipy.aquaipy import HDDevice
from aquaipy.error import ConnError, FirmwareError, MustBeParentError
from aquaipy.test.TestData import TestData


@pytest.mark.parametrize("power_response, primary_mac, max_mW", [
    (TestData.power_hydra26hd(), TestData.primary_mac_hydra26hd(), TestData.power_hydra26hd_max()),
    (TestData.power_primehd(), TestData.primary_mac_primehd(), TestData.power_primehd_max())
    ])
def test_HDDevice_init(power_response, primary_mac, max_mW):

    device = HDDevice(power_response["devices"][0], primary_mac)

    assert device.is_primary
    assert device.max_mW == max_mW


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
def test_HDDevice_covert_to_intensity(power_response, primary_mac, percentage, result_intensities):

    device = HDDevice(power_response["devices"][0], primary_mac)

    for color in TestData.get_colors():

        assert result_intensities[color] == device.convert_to_intensity(color, percentage)

