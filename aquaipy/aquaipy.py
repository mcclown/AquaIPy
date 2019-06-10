#
#   Copyright 2018 Stephen Mc Gowan <mcclown@gmail.com>
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""Module for working with the AquaIllumination range of lights."""

import asyncio
# pylint: disable=no-name-in-module,import-error
from distutils.version import StrictVersion
from enum import Enum
import json

import aiohttp

from aquaipy.error import ConnError, FirmwareError, MustBeParentError

MIN_SUPPORTED_AI_FIRMWARE_VERSION = "2.0.0"
MAX_SUPPORTED_AI_FIRMWARE_VERSION = "2.5.1"


class Response(Enum):
    """Response codes, for the AquaIPy methods."""

    Success = 0
    Error = 1
    NoSuchColour = 2
    InvalidBrightnessValue = 3
    PowerLimitExceeded = 4
    AllColorsMustBeSpecified = 5
    InvalidData = 6


class HDDevice:
    """A class for handling the conversion of data for a device."""

    def __init__(self, raw_data, primary_mac_address=None):
        """Initialise a class from the given input raw device data.

        :param raw_data: Raw device data, as returned by the AI API.
        :param primary_mac_address: The primary device MAC address.
        :type raw_data: json
        :type primary_mac_address: str
        """
        self._primary_mac_address = primary_mac_address
        self._mac_address = raw_data['serial_number']
        self._mw_norm = {}
        self._mw_hd = {}
        self._max_mw = 0

        # Get the values for 100%
        for color, value in raw_data["normal"].items():
            self._mw_norm[color] = value

        # Get the values for HD
        for color, value in raw_data["hd"].items():
            self._mw_hd[color] = value

        self._max_mw = raw_data["max_power"]

    @property
    def is_primary(self):
        """Check is HDDevice object represents a parent light.

        :returns: true if parent, false if not
        :rtype: bool
        """
        return self._primary_mac_address == self._mac_address

    @property
    def mac_address(self):
        """Get devices MAC address/serial number.

        :returns: MAC address of device
        :rtype: str
        """
        return self._mac_address

    @property
    def max_mw(self):
        """Get the max mWatts supported power level for the device.

        :returns: max mWatts
        :rtype: int
        """
        return self._max_mw

    def convert_to_intensity(self, color, percentage):
        """Convert a percentage to the native AI API intensity value.

        The conversion is different for every color and model of light. The
        intensity to be returned will be bewtween 0-1000 for non-HD values and
        between 1000-2000 for HD (over 100%) values.

        :param color: the specified color to convert
        :type color: str
        :param percentage: the percentage to convert
        :type percentage: float

        :returns: intensity value (0-2000)
        :rtype: int
        """
        if percentage < 0:
            raise ValueError("Percentage must be greater than 0")
        elif 0 <= percentage <= 100:
            return round(percentage * 10)
        else:

            #                           HD_Percentage
            #  HD_Brightness_Value =    --------------  * 1000
            #                           Max_HD_Percent

            max_percentage = ((self._mw_hd[color])
                              / self._mw_norm[color]) * 100

            if percentage > max_percentage:
                raise ValueError("Percentage for {} must be between 0 and {}"
                                 .format(color, max_percentage))

            hd_percentage = percentage - 100

            hd_brightness_value = (hd_percentage
                                   / (max_percentage - 100)) * 1000

            return round(hd_brightness_value + 1000)

    def convert_to_percentage(self, color, intensity):
        """Convert the native AI API intensity value to a percentage.

        The conversion of the intensity value (0 - 2000) will be different
        for every color and light model.

        :param color: the specified color to convert
        :type color: str
        :param intensity: the specified color intensity (0-2000)
        :type intensity: int

        :returns: the resulting percentage
        :rtype: float
        """
        if intensity < 0 or intensity > 2000:
            raise ValueError("intensity must be between 0 and 2000")
        elif intensity <= 1000:
            return intensity/10
        else:

            #                  Brightness - 1000   HD_Max - Normal_Max
            #  HD_Percentage = ----------------- * ------------------- * 100
            #                         1000            Normal_Max_mW

            # Calculate max HD percentage available
            max_hd_percentage = (self._mw_hd[color]
                                 - self._mw_norm[color])/self._mw_norm[color]

            # Response from /color: First 1000 is for 0 -> 100%,
            # Second 1000 is for 100% -> Max HD%
            hd_in_use = (intensity - 1000) / 1000

            # Calculate total current percentage
            return 100 + (max_hd_percentage * hd_in_use * 100)

    def convert_to_mw(self, color, intensity):
        """Convert a given AI API native intensity value to the mWatt value.

        An input intesnity (0-2000), is converted to the equivalent mWatt
        value for that color channel, on the specified device. This will
        differ for each color channel and device type.

        :param color: the specified color to convert
        :type color: str
        :param intensity: the specified color intensity (0-2000)
        :type intensity: int

        :returns: the resulting mWatt value, for the given intensity
        :rtype: float
        """
        if intensity < 0 or intensity > 2000:
            raise ValueError("intensity must be between 0 and 2000")
        elif intensity <= 1000:
            return self._mw_norm[color] * (intensity/1000)
        else:

            #                                               intensity - 1000
            # HD mW in use = (HD Max mW - Norm Max mW)  *   ----------------
            #                                                     1000

            hd_in_use = (intensity - 1000)/1000
            hd_mw_in_use = hd_in_use * (self._mw_hd[color]
                                        - self._mw_norm[color])

            return self._mw_norm[color] + hd_mw_in_use


class AquaIPy:
    """A class that exposes the AquaIllumination Lights API."""

    # pylint: disable=too-many-instance-attributes
    # All attributes are required, in this case.
    # pylint: disable=too-many-public-methods

    def __init__(self, name=None, session=None, loop=None):
        """Initialise class, with an optional instance name.

        :param name: Instance name, not currently used for anything.
        :type name: str
        """
        self._host = None
        self._base_path = None
        self._mac_addr = None
        self._name = name
        self._product_type = None
        self._firmware_version = None
        self._primary_device = None
        self._other_devices = []

        self._loop = loop
        self._loop_is_local = True

        if self._loop is None:

            try:
                self._loop = asyncio.get_event_loop()
                self._loop_is_local = False
            except RuntimeError:
                self._create_new_event_loop()

        if self._loop.is_closed():
            self._create_new_event_loop()

        if session is None:
            self._session = aiohttp.ClientSession()
            self._session_is_local = True
        else:
            self._session = session
            self._session_is_local = False

    def connect(self, host, check_firmware_support=True):
        """Connect **AquaIPy** instance to a specifed AI light, synchronously.

        :param host: Hostname/IP of AI light, for paired lights this should be
            the parent light.
        :param check_firmware_support: Set to False to skip the firmware check
        :type check_firmware_support: bool

        ..  note:: It is **NOT** recommended to set
            *check_firmware_support=False*. Do so at your own risk!

        :raises FirmwareError: If the firmware version is unsupported.
        :raises ConnError: If unable to connect to specified AI light.
        :raises MustBeParentError: the specified host must be the parent
            light, if there are multiple lights linked.

        :Example:
            >>> from aquaipy import AquaIPy
            >>> ai = AquaIPy()
            >>> ai.connect("192.168.1.1")

        """
        return self._loop.run_until_complete(
            self.async_connect(host, check_firmware_support))

    async def async_connect(self, host, check_firmware_support=True):
        """Connect **AquaIPy** instance to a specified AI light.

        Also verifies connectivity and firmware version support.

        :param host: Hostname/IP of AI light, for paired lights this should be
            the parent light.
        :param check_firmware_support: Set to False to skip the firmware check
        :type check_firmware_support: bool

        ..  note:: It is **NOT** recommended to set
            *check_firmware_support=False*. Do so at your own risk!

        :raises FirmwareError: If the firmware version is unsupported.
        :raises ConnError: If unable to connect to specified AI light.
        :raises MustBeParentError: the specified host must be the parent
            light, if there are multiple lights linked.

        :Example:
            >>> from aquaipy import AquaIPy
            >>> ai = AquaIPy()
            >>> await ai.async_connect("192.168.1.1")

        """
        self._host = host
        self._base_path = 'http://' + host + '/api'

        await self._async_setup_device_details(check_firmware_support)

    def close(self):
        """Clean-up and close the underlying async dependancies..

        .. note:: There is no async method, as it is assumed if you are using
           async functions, you will use your own event loop and
           aiohttp.ClientSession and pass them in. This will close the client
           session and event loop, if they were created by this object, when
           it was initialised.
        """
        self._base_path = None

        if self._session_is_local:
            self._loop.run_until_complete(self._session.close())

        if self._loop_is_local:
            self._loop.stop()
            pending_tasks = asyncio.Task.all_tasks()
            self._loop.run_until_complete(asyncio.gather(*pending_tasks))
            self._loop.close()

    @property
    def mac_addr(self):
        """Get connected devices Mac Address/Serial Number.

        :returns: device mac address/serial number
        :rtype: str

        """
        return self._mac_addr

    @property
    def name(self):
        """Get device name.

        :returns: device name
        :rtype: str

        """
        return self._name

    @property
    def product_type(self):
        """Get product type.

        :returns: product type
        :rtype: str

        """
        return self._product_type

    @property
    def supported_firmware(self):
        """Check if current firmware is supported.

        :returns: status of firmware support
        :rtype: bool

        """
        return (StrictVersion(self._firmware_version) <=
                StrictVersion(MAX_SUPPORTED_AI_FIRMWARE_VERSION)) and \
               (StrictVersion(self._firmware_version) >=
                StrictVersion(MIN_SUPPORTED_AI_FIRMWARE_VERSION))

    @property
    def base_path(self):
        """Get base path of the AI API.

        :returns: base path
        :rtype: str

        """
        return self._base_path

    @property
    def firmware_version(self):
        """Get firmware version.

        :returns: firmware version
        :rtype: str

        """
        return self._firmware_version

    ##################
    # Internal Methods
    ##################
    def _validate_connection(self):
        """Verify connection, raise Error if not available."""
        if self._base_path is None:
            raise ConnError("Error connecting to host", self._host)

    def _create_new_event_loop(self):
        """Create a new asyncio event loop."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop_is_local = True

    async def _async_setup_device_details(self, check_firmware_support):
        """Verify connection to the device and populate device attributes."""
        r_data = None

        try:
            path = "{0}/{1}".format(self._base_path, "identity")
            async with self._session.get(path) as resp:

                r_data = await resp.json()
        except Exception:
            self._base_path = None

            import traceback
            traceback.print_exc()
            raise ConnError("Unable to connect to host", self._host)

        if r_data['response_code'] != 0:
            self._base_path = None
            raise ConnError(
                "Error getting response for device identity", self._host)

        self._mac_addr = r_data['serial_number']
        self._firmware_version = r_data['firmware']
        self._product_type = r_data['product']

        if check_firmware_support and not self.supported_firmware:
            self._base_path = None
            raise FirmwareError(
                "Support is not available for this version of the "
                + "AquaIllumination firmware yet.", self._firmware_version)

        if r_data['parent'] != "":
            self._base_path = None
            raise MustBeParentError(
                "Connected to non-parent device", r_data['parent'])

        await self._async_get_devices()

    async def _async_get_devices(self):
        """Populate the device attributes of the current class instance."""
        path = "{0}/{1}".format(self._base_path, "power")
        async with self._session.get(path) as resp:

            r_data = await resp.json()
            if r_data['response_code'] != 0:
                self._base_path = None
                raise ConnError(
                    "Unable to retrieve device details", self._host)

            self._primary_device = None
            self._other_devices = []

            for device in r_data['devices']:
                temp = HDDevice(device, self.mac_addr)

                if temp.is_primary:
                    self._primary_device = temp
                else:
                    self._other_devices.append(temp)

    async def _async_get_brightness(self):
        """Get raw intensity values back from API."""
        self._validate_connection()

        path = "{0}/{1}".format(self._base_path, "colors")
        async with self._session.get(path) as resp:

            r_data = await resp.json()

            if r_data["response_code"] != 0:
                return Response.Error, None

            del r_data["response_code"]

            return Response.Success, r_data

    async def _async_set_brightness(self, body):
        """Set raw intensity values, via AI API."""
        self._validate_connection()

        path = "{0}/{1}".format(self._base_path, "colors")
        async with self._session.post(path, json=body) as resp:

            r_data = await resp.json()

            if r_data["response_code"] != 0:
                return Response.Error

            return Response.Success

    #######################################################
    # Get/Set Manual Control (ie. Not using light schedule)
    #######################################################
    def get_schedule_state(self):
        """Check if light schedule is enabled/disabled, synchronously.

        :returns: Schedule Enabled (*True*) / Schedule Disabled (*False*) or
            *None* if there's an error
        :rtype: bool

        :raises ConnError: if there is no valid connection to a device,
            usually because a previous call to ``connect()`` has failed
        """
        return self._loop.run_until_complete(self.async_get_schedule_state())

    async def async_get_schedule_state(self):
        """Check if light schedule is enabled/disabled.

        :returns: Schedule Enabled (*True*) / Schedule Disabled (*False*) or
            *None* if there's an error
        :rtype: bool

        :raises ConnError: if there is no valid connection to a device,
            usually because a previous call to ``connect()`` has failed
        """
        self._validate_connection()
        path = "{0}/{1}".format(self._base_path, "schedule/enable")
        async with self._session.get(path) as resp:

            r_data = await resp.json()

            if r_data is None or r_data["response_code"] != 0:
                return None

            return r_data["enable"]

    def set_schedule_state(self, enable):
        """Enable/Disable the light schedule, synchronously.

        :param enable: Schedule Enable (*True*) / Schedule Disable (*False*)
        :type enable: bool
        :returns: Response.Success if it works, or a value indicating the
            error, if there is an issue.
        :rtype: Response

        :raises ConnError: if there is no valid connection to a device,
            usually because a previous call to ``connect()`` has failed
        """
        return self._loop.run_until_complete(
            self.async_set_schedule_state(enable))

    async def async_set_schedule_state(self, enable):
        """Enable/disable the light schedule.

        :param enable: Schedule Enable (*True*) / Schedule Disable (*False*)
        :type enable: bool
        :returns: Response.Success if it works, or a value indicating the
            error, if there is an issue.
        :rtype: Response

        :raises ConnError: if there is no valid connection to a device,
            usually because a previous call to ``connect()`` has failed
        """
        self._validate_connection()
        data = {"enable": enable}

        path = "{0}/{1}".format(self._base_path, "schedule/enable")
        async with self._session.put(path, data=json.dumps(data)) as resp:

            r_data = await resp.json()

            if r_data is None:
                return Response.Error

            if r_data['response_code'] != 0:
                return Response.Error

            return Response.Success

    ###########################
    # Color Control / Intensity
    ###########################

    def get_colors(self):
        """Get the list of valid colors for other methods, synchronously.

        :returns: list of valid colors or *None* if there's an error
        :rtype: list( color_1..color_n ) or None

        :raises ConnError: if there is no valid connection to a device,
            usually because a previous call to ``connect()`` has failed
        """
        return self._loop.run_until_complete(self.async_get_colors())

    async def async_get_colors(self):
        """Get the list of valid colors to pass to other colors methods.

        :returns: list of valid colors or *None* if there's an error
        :rtype: list( color_1..color_n ) or None

        :raises ConnError: if there is no valid connection to a device,
            usually because a previous call to ``async_connect()`` has failed
        """
        colors = []

        resp, data = await self._async_get_brightness()

        if resp != Response.Success:
            return None

        for color in data:
            colors.append(color)

        return colors

    def get_colors_brightness(self):
        """Get the current brightness of all color channels, synchronously.

        :returns: dictionary of color and brightness percentages, or *None* if
            there's an error
        :rtype: dict( color_1=percentage_1..color_n=percentage_n ) or None

        :raises ConnError: if there is no valid connection to a device,
            usually because a previous call to ``connect()`` has failed
        """
        return self._loop.run_until_complete(
            self.async_get_colors_brightness())

    async def async_get_colors_brightness(self):
        """Get the current brightness of all color channels.

        :returns: dictionary of color and brightness percentages, or *None* if
            there's an error
        :rtype: dict( color_1=percentage_1..color_n=percentage_n ) or None

        :raises ConnError: if there is no valid connection to a device,
            usually because a previous call to ``connect()`` has failed
        """
        colors = {}

        # Get current brightness, for each colour channel
        resp_b, brightness = await self._async_get_brightness()

        if resp_b != Response.Success:
            return None

        for color, value in brightness.items():
            colors[color] = self._primary_device.convert_to_percentage(
                color, value)

        return colors

    def set_colors_brightness(self, colors):
        """Set all colors to the specified color percentage, synchronously.

        :param colors: dictionary of colors and percentage values
        :type colors: dict( color_1=percentage_1..color_n=percentage_n )
        :returns: Response.Success if it works, or a value indicating the
            error, if there is an issue.
        :rtype: Response

        :raises ConnError: if there is no valid connection to a device,
            usually because a previous call to ``connect()`` has failed
        """
        return self._loop.run_until_complete(
            self.async_set_colors_brightness(colors))

    async def async_set_colors_brightness(self, colors):
        """Set all colors to the specified color percentage.

        ..  note:: All colors returned by *get_colors()* must be specified.

        :param colors: dictionary of colors and percentage values
        :type colors: dict( color_1=percentage_1..color_n=percentage_n )
        :returns: Response.Success if it works, or a value indicating the
            error, if there is an issue.
        :rtype: Response

        :raises ConnError: if there is no valid connection to a device,
            usually because a previous call to ``connect()`` has failed
        """
        # Need to add better validation here
        if len(colors) < len(await self.async_get_colors()):
            return Response.AllColorsMustBeSpecified

        intensities = {}
        mw_value = 0

        for color, value in colors.items():
            intensities[color] = self._primary_device.convert_to_intensity(
                color, value)

            mw_value += self._primary_device.convert_to_mw(
                color, intensities[color])

        if mw_value > self._primary_device.max_mw:
            print("Primary Device: mWatts exceeded - max: {} specified: {}"
                  .format(str(self._primary_device.max_mw), str(mw_value)))

            return Response.PowerLimitExceeded

        # Check if planned intensities will exceed any child devices max_mW
        # (only issue if there are two different device types paired)
        for device in self._other_devices:
            mw_value = 0

            for color, value in intensities.items():
                mw_value += device.convert_to_mw(color, value)

            if mw_value > device.max_mw:
                print("mWatts exceeded - device: {} max: {} specified: {}"
                      .format(device.mac_address, str(device.max_mw),
                              str(mw_value)))
                return Response.PowerLimitExceeded

        return await self._async_set_brightness(intensities)

    def patch_colors_brightness(self, colors):
        """Set specified colors to the given percentage values, sychronously.

        :param colors: Specify just the colors that should be updated
        :type colors: dict( color_1=percentage_1..color_n=percentage_n )
        :returns: Response.Success if it works, or a value indicating the
            error, if there is an issue.
        :rtype: Response

        :raises ConnError: if there is no valid connection to a device,
            usually because a previous call to ``connect()`` has failed
        """
        return self._loop.run_until_complete(
            self.async_patch_colors_brightness(colors))

    async def async_patch_colors_brightness(self, colors):
        """Set specified colors to the given percentage brightness.

        :param colors: Specify just the colors that should be updated
        :type colors: dict( color_1=percentage_1..color_n=percentage_n )
        :returns: Response.Success if it works, or a value indicating the
            error, if there is an issue.
        :rtype: Response

        :raises ConnError: if there is no valid connection to a device,
            usually because a previous call to ``connect()`` has failed
        """
        if len(colors) < 1:
            return Response.InvalidData

        brightness = await self.async_get_colors_brightness()

        if brightness is None:
            return Response.Error

        for color, value in colors.items():
            brightness[color] = value

        return await self.async_set_colors_brightness(brightness)

    def update_color_brightness(self, color, value):
        """Update a given color by the specified brightness, synchronously.

        :param color: color to change
        :param value: value to change percentage by
        :type color: str
        :type value: float
        :returns: Response.Success if it works, or a value indicating the
            error, if there is an issue.
        :rtype: Response

        :raises ConnError: if there is no valid connection to a device,
            usually because a previous call to ``connect()`` has failed.
        """
        return self._loop.run_until_complete(
            self.async_update_color_brightness(color, value))

    async def async_update_color_brightness(self, color, value):
        """Update a given color by the specified brightness percentage.

        :param color: color to change
        :param value: value to change percentage by
        :type color: str
        :type value: float
        :returns: Response.Success if it works, or a value indicating the
            error, if there is an issue.
        :rtype: Response

        :raises ConnError: if there is no valid connection to a device,
            usually because a previous call to ``connect()`` has failed.
        """
        if not color:
            return Response.InvalidData

        # No change required
        if value == 0:
            return Response.Success

        brightness = await self.async_get_colors_brightness()

        if brightness is None:
            return Response.Error

        brightness[color] += value

        return await self.async_set_colors_brightness(brightness)
