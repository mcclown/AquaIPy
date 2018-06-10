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


class AquaIPy:
    """A class to encapsulate all functions of a AquaIllumination Prime HD & Hydra HD range of Lights 
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

        r = requests.get(self._base_path + "/identity")
        
        r_data = None
        r_data = r.json()
        
        if r_data['response_code'] != 0:
            #Clear down base_path, if setup device fails
            self._base_path = None
            raise ConnError("Error connecting to host", self._host)
            
        self._mac_addr = r_data['serial_number']
        self._firmware_version = r_data['firmware']
        self._product_type = r_data['product']
        
        if check_firmware_support and not self.supported_firmware:
            raise FirmwareError("Support is not available for this version of the AquaIllumination firmware yet.", self._firmware_version)

        if r_data['parent'] != "":
            raise MustBeParentError("Connected to non-parent device", r_data['parent'])

    
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

            
    def _get_mW_limits(self):
        """
        Get mWatts limits in normal mode & HD mode, for each color channel. Also retrieve overall max mW available.
        """
        
        self._validate_connection()
        r = requests.get(self._base_path + "/power")
    
        r_data = None
        
        mW_norm = {}
        mW_hd = {}
        total_max_mW = 0

        r_data = r.json()
    
        if r_data["response_code"] != 0:
            return Response.Error, None, None, None
 
        #Only handling the first device for the moment. In mixed HD & non-HD setups, devices are limited to non-HD modes, as far as I can tell.

        #Get the values for 100%
        for color, value in r_data["devices"][0]["normal"].items():
            mW_norm[color] = value
        
        try:
            #Get the values for HD
            for color, value in r_data["devices"][0]["hd"].items():
                mW_hd[color] = value

            #Don't know if this value is present on non-HD devices, until I can test.
            total_max_mW = r_data["devices"][0]["max_power"]
            
        except Exception:
            #Potentially handle non-HD AI devices? #ToTest
            print("Unable to retrieve HD mW values for device")
        
        return Response.Success, mW_norm, mW_hd, total_max_mW


            
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
        
        resp_l = mW_norm = mW_hd = total_max_mW = None
 
        for color, value in brightness.items():
            #Calculate the %power
            
            if value <= 1000:
                colors[color] = value/10
            else:
                #Should never hit this case for a non-HD AI device. #ToTest

                #                       Brightness Value - 1000         HD_Max_mW - Normal_Max_mW  
                #   HD_Percentage =     -----------------------     *   -------------------------   *   100
                #                               1000                            Normal_Max_mW

                #Only retrieve this info once, if it's required.
                if resp_l == None:
                    resp_l, mW_norm, mW_hd, total_max_mW = self._get_mW_limits()

                    if resp_l != Response.Success:
                        return None

                #Calculate max HD percentage available
                max_hd_percentage = (mW_hd[color] - mW_norm[color]) / mW_norm[color]

                #Response from /color: First 1000 is for 0 -> 100%, Second 1000 is for 100% -> Max HD% 
                hd_in_use = (value - 1000) / 1000  

                #Calculate total current percentage
                colors[color] = 100 + (max_hd_percentage * hd_in_use * 100)

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
        if len(colors) == 0 or len(colors) < len(self.get_colors()):
            return Response.AllColorsMustBeSpecified

            
        response, mW_norm, mW_hd, total_mW_limit = self._get_mW_limits()

        if response != Response.Success:
            return response
        
        specified_mW = 0

        for color, value in colors.items():

            if value <= 0:
                colors[color] = 0
            elif 0 < value <= 100:
                colors[color] = round(value * 10)

            else:

                #                           HD_Percentage       
                #  HD_Brightness_Value =    --------------  * 1000
                #                           Max_HD_Percent
                
                hd_percentage = value - 100
                max_hd_percentage = ((mW_hd[color] - mW_norm[color]) / mW_norm[color]) * 100
                
                hd_brightness_value = (hd_percentage / max_hd_percentage) * 1000

                colors[color] = round(hd_brightness_value + 1000)

            specified_mW += mW_norm[color] * (value / 100)

        if specified_mW > total_mW_limit:
            print("mWatts exceeded - Max:" + str(total_mW_limit) + " Specified:" + str(specified_mW))
            return Response.PowerLimitExceeded

        return self._set_brightness(colors)
    
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


