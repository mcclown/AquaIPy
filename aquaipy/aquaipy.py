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


from enum import Enum
import requests
import json
import traceback
from distutils.version import StrictVersion
from aquaipy.error import ConnError, FirmwareError, MustBeParentError

MIN_SUPPORTED_AI_FIRMWARE_VERSION = "2.0.0"
MAX_SUPPORTED_AI_FIRMWARE_VERSION = "2.2.0"


class Response(Enum):
    """
    Response codes, for the AquaIPy methods
    """

    Success = 0
    Error = 1
    NoSuchColour = 2
    InvalidBrightnessValue = 3
    PowerLimitExceeded = 4
    AllColorsMustBeSpecified = 5
    InvalidData = 6


class HDDevice:
    """A class that is created with the configuration of one of the HD range of lights, an handles conversions of data.
    """

    def __init__(self, raw_data, primary_mac_address = None):

        self._primary_mac_address = primary_mac_address
        self._mac_address = raw_data['serial_number']
        self._mW_norm = {}
        self._mW_hd = {}
        self._max_mW = 0

        #Get the values for 100%
        for color, value in raw_data["normal"].items():
            self._mW_norm[color] = value
        
        #Get the values for HD
        for color, value in raw_data["hd"].items():
            self._mW_hd[color] = value

        self._max_mW = raw_data["max_power"]
            

    @property
    def is_primary(self):
        return self._primary_mac_address == self._mac_address


    @property
    def max_mW(self):
        return self._max_mW


    def convert_to_intensity(self, color, percentage):

        if percentage < 0:
            raise ValueError("Percentage must be greater than 0")
        elif 0 <= percentage <= 100:
            return round(percentage * 10)
        else:

            #                           HD_Percentage       
            #  HD_Brightness_Value =    --------------  * 1000
            #                           Max_HD_Percent
            
            max_percentage = ((self._mW_hd[color]) / self._mW_norm[color]) * 100

            if percentage > max_percentage:
                raise ValueError("Percentage for {} must be between 0 and {}".format(color, max_percentage))
            
            hd_percentage = percentage - 100
            hd_brightness_value = (hd_percentage / (max_percentage - 100)) * 1000

            return round(hd_brightness_value + 1000)


    def convert_to_percentage(self, color, intensity):
        
        if intensity < 0 or intensity > 2000:
            raise ValueError("intensity must be between 0 and 2000")
        elif intensity <= 1000:
            return intensity/10
        else:

            #                       Brightness Value - 1000         HD_Max_mW - Normal_Max_mW  
            #   HD_Percentage =     -----------------------     *   -------------------------   *   100
            #                               1000                            Normal_Max_mW


            #Calculate max HD percentage available
            max_hd_percentage = (self._mW_hd[color] - self._mW_norm[color]) / self._mW_norm[color]

            #Response from /color: First 1000 is for 0 -> 100%, Second 1000 is for 100% -> Max HD% 
            hd_in_use = (intensity - 1000) / 1000  

            #Calculate total current percentage
            return 100 + (max_hd_percentage * hd_in_use * 100)


    def convert_to_mW(self, color, intensity):
        
        if intensity < 0 or intensity > 2000:
            raise ValueError("intensity must be between 0 and 2000")
        elif intensity <= 1000:
            return self._mW_norm[color] * (intensity/1000)
        else:

            #                                                   intensity - 1000
            # HD mW in use = (HD Max mW - Norm Max mW)    *     ----------------  
            #                                                         1000

            hd_in_use = (intensity - 1000)/1000
            hd_mW_in_use = hd_in_use * (self._mW_hd[color] - self._mW_norm[color])

            return self._mW_norm[color] + hd_mW_in_use


class AquaIPy:
    """A class to the AquaIllumination API, for their range of lights 
    """
    
    def __init__(self, name = None):
    
        self._base_path = None 
        self._mac_addr = None
        self._name = name
        self._product_type = None
        self._firmware_version = None
    
    
    def connect(self, host, check_firmware_support=True):
        """Connect **AquaIPy** instance to a specified AI light. Also verfies connectivity and firmware version.

        :param host: Hostname/IP address of AI light, for paired lights this should be the parent light.
        :param check_firmware_support: Set to False to skip the firmware check.
        :type check_firmware_support: bool
        
        ..  note:: It is **NOT** recommended to set *check_firmware_support=False*. Do so at your own risk!

        :raises FirmwareError: If the firmware version is unsupported.
        :raises ConnError: If unable to connect to specified AI light.
        :raises MustBeParentError: the specified host must be the parent light, if there are multiple lights linked.
        
        :Example:
            >>> from aquaipy import AquaIPy
            >>> ai = AquaIPy()
            >>> ai.connect("192.168.1.1")
        
        """

        self._host = host
        self._base_path = 'http://' + host + '/api'

        self._setup_device_details(check_firmware_support)
        
        
    @property
    def mac_addr(self):
        """Gets connected devices Mac Address/Serial Number.
        
        :returns: device mac address/serial number
        :rtype: str

        """
        return self._mac_addr

    @property
    def name(self):
        """Gets device name

        :returns: device name
        :rtype: str

        """
        return self._name
        
    @property
    def product_type(self):
        """Gets product type

        :returns: product type
        :rtype: str
        
        """
        return self._product_type
    
    @property
    def supported_firmware(self):
        """Checks if current firmware is supported

        :returns: status of firmware support
        :rtype: bool

        """
        return (StrictVersion(self._firmware_version) <= StrictVersion(MAX_SUPPORTED_AI_FIRMWARE_VERSION)) and (StrictVersion(self._firmware_version) >= StrictVersion(MIN_SUPPORTED_AI_FIRMWARE_VERSION))

    @property
    def base_path(self):
        """Get base path of the AI API
        
        :returns: base path
        :rtype: str

        """
        return self._base_path

    @property
    def firmware_version(self):
        """Get firmware version

        :returns: firmware version
        :rtype: str

        """
        return self._firmware_version
   

    ##################
    # Internal Methods
    ##################
    def _validate_connection(self):
        """Verify connectivity, raise Error if not availale"""
    
        if self._base_path == None:
            raise ConnError("Error connecting to host", self._host)


    def _setup_device_details(self, check_firmware_support):
        """
        Verify connectivity to the device and populate device attributes
        """

        r_data = None
        
        try:
            r = requests.get(self._base_path + "/identity")
        
            r_data = None
            r_data = r.json()
        except:
            self._base_path = None
            raise ConnError("Unable to connect to host", self._host)
        
        if r_data['response_code'] != 0:
            self._base_path = None
            raise ConnError("Error getting response for device identity", self._host)
            
        self._mac_addr = r_data['serial_number']
        self._firmware_version = r_data['firmware']
        self._product_type = r_data['product']
        
        if check_firmware_support and not self.supported_firmware:
            self._base_path = None
            raise FirmwareError("Support is not available for this version of the AquaIllumination firmware yet.", self._firmware_version)

        if r_data['parent'] != "":
            self._base_path = None
            raise MustBeParentError("Connected to non-parent device", r_data['parent'])

        self._get_devices()


    def _get_devices(self):

        r = requests.get(self._base_path + "/power")
        r_data = r.json()
        
        if r_data['response_code'] != 0:
            self._base_path = None
            raise ConnError("Unable to retrieve device details", self._host)
        
        self._primary_device = None
        self._other_devices = []

        for device in r_data['devices']:

            temp = HDDevice(device, self.mac_addr)

            if temp.is_primary:
                self._primary_device = temp
            else:
                self._other_devices.append(temp)
   
    
    def _get_brightness(self):
        """
        Get raw intensity values back from API
        """
        
        self._validate_connection()
        r = requests.get(self._base_path + "/colors")
        
        r_data = None
        r_data = r.json()
            
        if r_data["response_code"] != 0:
            return Response.Error, None
 
        del r_data["response_code"]

        return Response.Success, r_data

        
    def _set_brightness(self, body):
        """
        Set raw intensity values, via AI API
        """
        
        self._validate_connection() 
        r = requests.post(self._base_path + "/colors", json = body)

        r_data = None
        r_data = r.json()

        if r_data["response_code"] == 0:
            return Response.Success
        else:
            return Response.Error
            
            
    #######################################################
    # Get/Set Manual Control (ie. Not using light schedule)
    #######################################################
        
    def get_schedule_state(self):
        """Check if light schedule is enabled/disabled

        :returns: Schedule Enabled (*True*) / Schedule Disabled (*False*) or *None* if there's an error
        :rtype: bool
        
        :raises ConnError: if there is no valid connection to a device, usually because a previous call to ``connect()`` has failed
       
        """
        
        self._validate_connection()
        r = requests.get(self._base_path + '/schedule/enable')
        r_data = None 
        
        try:
            r_data = r.json()
            
            if r_data["response_code"] != 0:
                return None
                
        except Exception as ex:
            return None

        return r_data["enable"]

    
    def set_schedule_state(self, enable):
        """Enable/disable the light schedule

        :param enable: Schedule Enable (*True*) / Schedule Disable (*False*)
        :type enable: bool
        :returns: Response.Success if it works, or a value indicating the error, if there is an issue.
        :rtype: Response

        :raises ConnError: if there is no valid connection to a device, usually because a previous call to ``connect()`` has failed
        
        """
        
        self._validate_connection() 
        data = {"enable": enable}
        r = requests.put(self._base_path + "/schedule/enable", data = json.dumps(data) )

        r_data = None
        
        try:
            r_data = r.json()
            
            if r_data['response_code'] != 0:
                return Response.Error
            
        except Exception as ex:
            print("Unable to set light control: ", ex)
            return Response.Error

        return Response.Success

        
    ###########################
    # Color Control / Intensity
    ###########################
    
    def get_colors(self):
        """Get the list of valid colors to pass to other colors methods
        
        :returns: list of valid colors or *None* if there's an error
        :rtype: list( color_1..color_n ) or None

        :raises ConnError: if there is no valid connection to a device, usually because a previous call to ``connect()`` has failed
        
        """
        
        colors = []

        resp, data = self._get_brightness()
            
        if resp != Response.Success:
            return None

        for color in data:
            colors.append(color)

        return colors
   

    def get_colors_brightness(self):
        """Get the current brightness of all color channels.

        :returns: dictionary of color and brightness percentages, or *None* if there's an error
        :rtype: dict( color_1=percentage_1..color_n=percentage_n ) or None

        :raises ConnError: if there is no valid connection to a device, usually because a previous call to ``connect()`` has failed
        
        """
        
        colors = {}

        
        #Get current brightness, for each colour channel
        resp_b, brightness = self._get_brightness()

        if resp_b != Response.Success:
            return None
        
        for color, value in brightness.items():
            
            colors[color] = self._primary_device.convert_to_percentage(color, value)

        return colors


    def set_colors_brightness(self, colors):
        """Set all colors to the specified color percentage.
            
        ..  note:: All colors returned by *get_colors()* must be specified.

        :param colors: dictionary of colors and percentage values
        :type colors: dict( color_1=percentage_1..color_n=percentage_n )
        :returns: Response.Success if it works, or a value indicating the error, if there is an issue.
        :rtype: Response

        :raises ConnError: if there is no valid connection to a device, usually because a previous call to ``connect()`` has failed
        
        """
        
        #Need to add better validation here
        if len(colors) < len(self.get_colors()):
            return Response.AllColorsMustBeSpecified

        intensities = {}
        mW_value = 0
            
        for color, value in colors.items():
            
            intensities[color] = self._primary_device.convert_to_intensity(color, value)
            mW_value += self._primary_device.convert_to_mW(color, intensities[color])

        if mW_value > self._primary_device.max_mW:
            print("Primary Device: mWatts exceeded - max: {} specified: {}".format(str(self._primary_device.max_mW), str(mW_value)))
            return Response.PowerLimitExceeded

        #Check if planned intensities will exceed any child devices max_mW (only issue if there are mixed devices paired, ie. Hydra26HD and PrimeHD)
        for device in self._other_devices:
            mW_value = 0

            for color, value in intensities.items():
                mW_value += device.convert_to_mW(color, value)

            if mW_value > device.max_mW:
                print("mWatts exceeded - max: {} specified: {}".format(str(device.max_mW), str(mW_value)))
                return Response.PowerLimitExceeded

        return self._set_brightness(intensities)
   

    def patch_colors_brightness(self, colors):
        """Set specified colors, to the specified percentage brightness.

        :param colors: Specify just the colors that should be updated
        :type colors: dict( color_1=percentage_1..color_n=percentage_n )
        :returns: Response.Success if it works, or a value indicating the error, if there is an issue.
        :rtype: Response

        :raises ConnError: if there is no valid connection to a device, usually because a previous call to ``connect()`` has failed
        
        """

        if len(colors) < 1:
            return Response.InvalidData

        response, brightness = self.get_colors_brightness()

        for color, value in colors.items():
            brightness[color] = value

        return self.set_colors_brightness(brightness)

    
    def update_color_brightness(self, color, value):
        """Update a given color by the specified brightness percentage.
        
        :param color: color to change
        :param value: value to change percentage by
        :type color: str
        :type value: float
        :returns: Response.Success if it works, or a value indicating the error, if there is an issue.
        :rtype: Response

        :raises ConnError: if there is no valid connection to a device, usually because a previous call to ``connect()`` has failed
        
        """
        
        if len(color)==0:
            return Response.InvalidData

        #No change required
        if value == 0:
            return Response.Success

        response, brightness = self.get_colors_brightness()
        
        brightness[color] += value

        return self.set_colors_brightness(brightness)


