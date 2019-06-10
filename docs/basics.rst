Basics
======

Here are some basic details of how to use this library.

Install
-------

The easiest method to install ``AquaIPy`` is using ``pip``.::
        
        $ pip install AquaIPy


Connecting to your AI light
---------------------------

Connecting to your AI light is simple. For the case where your AI light is accessible at the IP ``192.168.1.10``, all 
that is required is.::

        >>> from aquaipy import AquaIPy
        >>> ai = AquaIPy()
        >>> await ai.async_connect("192.168.1.10") 

This will verify connectivity to the light and check the firmware version is supported. In the case where you have multiple
lights paired together, AquaIPy expects to be connected to the parent/primary light, of the group and will give an error if
it is connected to one of the child lights.


Getting/Setting the schedule state
----------------------------------

Working off the assumption that the majority of lights will be currently running on a schedule already, it's important 
to be able to disable and enable the schedule. If you don't disable the schedule and try to set the colors with the 
library, the colors will only change for a second and then change back to the schedule. 

Getting the schedule state is easy.::

        >>> await ai.async_get_schedule_state()
        True

Setting it is easy as well.::

        >>> await ai.async_set_schedule_state(False)
        <Response.Success: 0>



Playing around with color
-------------------------

The AI lights provide a number of color channels. The ``AquaIPy`` library provides a range of different functions to 
manage colors.


Getting the colors
``````````````````

The API will only accept certain colors, you can get the ``list`` of valid colors with the following call.::

        >>> await ai.async_get_colors()
        ['deep_red', 'royal', 'cool_white', 'violet', 'green', 'blue', 'uv']


It's also possible to retrieve the list of the colours and their current state with the following call.::

        >>> await ai.async_get_colors_brightness()
        {'blue': 18.7,
         'cool_white': 4.4,
         'deep_red': 1.0,
         'green': 1.3,
         'royal': 18.4,
         'uv': 46.3,
         'violet': 46.8}


Setting the colors
``````````````````

The API also provides a number of different ways to set, patch all colors, as well as increase/decrease a single 
color channel.

All colors can be set in one call to the function below, by providing a ``dict`` of colors and their percentage 
value.::

        >>> await ai.async_set_colors_brightness(all_colors)
        <Response.Success: 0>

It also possible to modify only a subset of the colors by providing them as a ``dict``.::

        >>> await ai.async_patch_colors_brightness(subset_colors)
        <Response.Success: 0>

Lastly, it's possible to update a given color channel by a specified percentage.::

        >>> await ai.async_update_color_brightness('cool_white', 33.333)
        <Response.Success: 0>
        >>> await ai.async_update_color_brightness('deep_red', -15.2)
        <Response.Success: 0>


Response Codes
``````````````

The library can return a number of response codes as ``Response`` objects. The respone codes that you should be aware 
of are below. If any of the these error response codes are returned, then the call will have failed and no changes will 
have been made:

* ``Response.AllColorsMustBeSpecified`` - returned when a call to ``async_set_colors_brightness()`` doesn't include all colors.
* ``Response.PowerLimitExceeded`` - returned when a call to one of the methods that updates the colors, would have exceeded the max wattage allowed for the targeted light. 
* ``Response.InvalidData`` - returned when invalid data is supplied to one of the methods that updates the colors.




