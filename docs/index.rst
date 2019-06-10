.. aquaipy documentation master file, created by
   sphinx-quickstart on Sat Jun  9 00:34:26 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to aquaipy's documentation!
===================================


Introduction
------------

AquaIPy exposes the functionality that is usually available, via the AquaIllumination mobile phone app or web app,
for the Prime HD and Hydra HD ranges of aquarium lights. AquaIPy is written with full async support, using asyncio
but also provides synchronous wrappers for all functions.

This has been tested and validated with a Prime HD and a Hydra 26HD. It should work with a Hydra 52HD but I don't 
own one to test against, contact me if you have one and you are willing to help me validate the library. In theory 
it can be extended to support the non-HD models but I haven't had access to those models for testing yet. There is 
some code in place, that may handle them but I would again need access to them to validate. If you have one, and 
are willing to help with testing, let me know.

.. note:: I have tried my best to validate, and test, this functionality to make sure there were no issues but using this could, and most likely will, invalidate the warranty that AquaIllumination provides, and could do damange to your light. Using this library is entirely at your own risk. This software is provided, *AS IS*, without any warranties or conditions of any kinds. I will not be held responsible for any damages. This library is released under the Apache Version 2.0 license, which states the same and a copy can be found with the source code. 


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   Basics <basics>
   API <aquaipy>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
