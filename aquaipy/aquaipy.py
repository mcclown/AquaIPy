"""

   Copyright 2018 Stephen Mc Gowan <mcclown@gmail.com>

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

"""

from enum import Enum
import requests
import json
import traceback
from distutils.version import StrictVersion

MIN_SUPPORTED_AI_FIRMWARE_VERSION = "2.0.0"
MAX_SUPPORTED_AI_FIRMWARE_VERSION = "2.2.0"

class Response(Enum):

    Success = 0
    Error = 1
    NoSuchColour = 2
    InvalidBrightnessValue = 3
    PowerLimitExceeded = 4
    AllColorsMustBeSpecifed = 5
    InvalidData = 6


class AquaIPy:
    
    def __init__(self, name = None):
    
        self._base_path = None 
        self._mac_addr = None
        self._name = name
        self._product_type = None
        self._firmware_version = None
        
    @property
    def mac_addr(self):
        return self._mac_addr

    @property
    def name(self):
        return self._name
        
    @property
    def product_type(self):
        return self._product_type
    
    @property
    def supported_firmware(self):
        return (StrictVersion(self._firmware_version) <= StrictVersion(MAX_SUPPORTED_AI_FIRMWARE_VERSION)) and (StrictVersion(self._firmware_version) >= StrictVersion(MIN_SUPPORTED_AI_FIRMWARE_VERSION))

    @property
    def base_path(self):
        return self._base_path

    @property
    def firmware_version(self):
        return self._firmware_version

    ##################
    # Internal Methods
    ##################
    
    def _setup_device_details(self):
        """
        Verify connectivity to the device and populate device attributes
        """
    
        r = requests.get(self._base_path + "/identity")
        
        r_data = None
        r_data = r.json()
        
        if r_data['response_code'] != 0:
            raise ConnectionError("Error connecting to host [" + self._host + "]")
            
        self._mac_addr = r_data['serial_number']
        self._firmware_version = r_data['firmware']
        self._product_type = r_data['product']

    
    def _get_brightness(self):
        """
        Get raw intensity values back from API
        """
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
        
        r = requests.post(self._base_path + "/colors", json = body)

        r_data = None
        r_data = r.json()

        if r_data["response_code"] == 0:
            return Response.Success
        else:
            print(r_data)
            return Response.Error

            
    def _get_mW_limits(self):
        """
        Get mWatts limits in normal mode & HD mode, for each color channel. Also retrieve overall max mW available.
        """

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


    def connect(self, host):

        self._host = host
        self._base_path = 'http://' + host + '/api'

        self._setup_device_details()
        
        if not self.supported_firmware:
            raise NotImplementedError("Support is not available for this version of the AquaIllumination firmware yet.")

        
    #######################################################
    # Get/Set Manual Control (ie. Not using light schedule)
    #######################################################
        
    def get_schedule_state(self):
        """get_schedule_state
        Get the current status of light schedule control (enabled/disabled).
        """

        r = requests.get(self._base_path + '/schedule/enable')
        r_data = None 
        
        try:
            r_data = r.json()
            
            if r_data['response_code'] != 0:
                return Response.Error, r_data
                
        except Exception as ex:
            return None

        return r_data["enable"]

    
    def set_schedule_state(self, enable):
        """set_schedule_state
        Enable or disable the light schedule
        """
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
        """get_colors
        Get the list of valid colors to pass to other colors methods. # noqa: E501
        :rtype: List[str]
        """
        
        colors = []

        try:
        
            resp, data = self._get_brightness()
            
            if resp != Response.Success:
                return resp, None

            for color in data:
                colors.append(color)

        except Exception as ex:
            print("Error processing get_colors response: ", ex)
            return Response.Error, None
        
        return Response.Success, colors
    
    def get_color_brightness(self):
        """get_color_brighness
        Get the current brightness of all color channels.
        """
        
        colors = {}

        try:
            
            #Get current brightness, for each colour channel
            resp_b, brightness = self._get_brightness()

            if resp_b != Response.Success:
                return resp_b, None
            
            #Get the power limits that represent 100%
            resp_l = mW_norm = mW_hd = total_max_mW = None
     
            for color, value in brightness.items():
                #Calculate the %power
                
                if value <= 1000:
                    colors[color] = round(value/10)
                else:
                    #Should never hit this case for a non-HD AI device. #ToTest

                    #                       Brightness Value - 1000         HD_Max_mW - Normal_Max_mW  
                    #   HD_Percentage =     -----------------------     *   -------------------------   *   100
                    #                               1000                            Normal_Max_mW

                    #Only retrieve this info once, if it's required.
                    if resp_l == None:
                        resp_l, mW_norm, mW_hd, total_max_mW = self._get_mW_limits()

                        if resp_l != Response.Success:
                            return resp_l, None

                    #Calculate max HD percentage available
                    max_hd_percentage = (mW_hd[color] - mW_norm[color]) / mW_norm[color]

                    #Response from /color: First 1000 is for 0 -> 100%, Second 1000 is for 100% -> Max HD% 
                    hd_in_use = (value - 1000) / 1000  

                    #Calculate total current percentage
                    colors[color] = round(100 + (max_hd_percentage * hd_in_use * 100))

        except Exception as ex:
            print("Error processing get_color_brightness response: ", traceback.format_exc())
            return Response.Error, None
        
        return Response.Success, colors

    def set_color_brightness(self, colors):
        """set_color_brightness
        Update all colors to the specified color percentage. All colors must be specified.
        """
        
        #Need to add better validation here
        if len(colors) == 0 or len(colors) < len(self.get_colors()):
            return Response.InvalidData

        try:
            
            response, mW_norm, mW_hd, total_mW_limit = self._get_mW_limits()
            
            specified_mW = 0

            for color, value in colors.items():

                if value <= 0:
                    colors[color] = 0
                elif 0 < value <= 100:
                    colors[color] = value * 10

                else:
 
                    #                           HD_Percentage       
                    #  HD_Brightness_Value =    --------------  * 1000
                    #                           Max_HD_Percent
                    
                    #top = 10 * (value - 100) * mW_norm[color]
                    #bottom = mW_hd[color] - mW_norm[color]

                    hd_percentage = value - 100
                    max_hd_percentage = ((mW_hd[color] - mW_norm[color]) / mW_norm[color]) * 100
                    
                    hd_brightness_value = (hd_percentage / max_hd_percentage) * 1000

                    #Floor calculation, to force round down.
                    colors[color] = int(hd_brightness_value + 1000)

                specified_mW += mW_norm[color] * (value / 100)

            if specified_mW > total_mW_limit:
                print("mWatts exceeded - Max:" + str(total_mW_limit) + " Specified:" + str(specified_mW))
                return Response.PowerLimitExceeded

            return self._set_brightness(colors)

        except Exception as ex:
            print("Error processing set_color_brightness", traceback.format_exc())
            return Response.Error

        
    def patch_color_brightness(self, colors):
        """patch_color_brightness
        Update to the specified color percentage brightness.
        """

        if len(colors) < 1:
            return Response.InvalidData

        try:
            response, brightness = self.get_color_brightness()

            for color, value in colors.items():
                brightness[color] = value

            return self.set_color_brightness(brightness)

        except Exception as ex:
            print("Error processing patch_color_brightness response: ", traceback.format_exc())
            return Response.Error
     
    
    def update_color_brightness(self, colors):
        """update_color_brightness
        Update a given color by the specified brightness percentage.
        """
        
        if len(colors) < 1:
            return Response.InvalidData

        try:
            response, brightness = self.get_color_brightness()
            
            for color, value in colors.items():
                brightness[color] += value

            return self.set_color_brightness(brightness)

        except Exception as ex:
            print("Error processing update_color_brightness response: ", traceback.format_exc())
            return Response.Error
    

