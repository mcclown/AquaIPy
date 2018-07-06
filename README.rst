AquaIPy
=======

|Build Status| |Coverage Status|

A module for working with the AquaIllumination range of aquarium lights.
The following functions are currently supported

-  Support for the HD range of lights, including single lights, paired
   lights (of the same model) and paired lights (with mixed models)
-  Enabling/Disabling the schedule
-  Querying the current brightness of the lights
-  Setting the brightness of the lights

This library has been primarily tested with Prime HD and Hydra 26HD
lights, as that is what the author owns. Hydra 52 HDs should work but
haven't been validated. Also the non-HD range of lights are not
currently supported, although it should be possible to add that support.
If you would like to help fix either of these cases, please contact me
via GitHub or by email.

This module is in no way endorsed by AquaIllumination and you use it at
your own risk. It could, and probably does, invalidate your warranty.

Generated documentation can be found
`here <http://aquaipy.readthedocs.io/en/latest/>`__

Quickstart
----------

Install aquaipy using ``pip``: ``$ pip install aquaipy``. Once that is
complete you can import the AquaIPy class and connect to your lights.

.. code:: python

    >>> from aquaipy import AquaIPy
    >>> ai = AquaIPy()
    >>> ai.connect("192.168.1.100")

Once the class is initialised and connected, you can query and update
your light.

.. code:: python

    >> ai.get_colors_brightness()
    {'blue': 18.7,
     'cool_white': 4.4,
     'deep_red': 1.0,
     'green': 1.3,
     'royal': 18.4,
     'uv': 46.3,
     'violet': 46.8}
    >>> ai.update_color_brightness('cool_white', 33.333)
    <Response.Success: 0>
    >>> ai.update_color_brightness('deep_red', -15.2)
    <Response.Success: 0>

Issues & Questions
------------------

If you have any issues, or questions, please feel free to contact me, or
open an issue on GitHub

.. |Build Status| image:: https://travis-ci.org/mcclown/AquaIPy.svg?branch=master
   :target: https://travis-ci.org/mcclown/AquaIPy
.. |Coverage Status| image:: https://coveralls.io/repos/mcclown/AquaIPy/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/mcclown/AquaIPy?branch=master
