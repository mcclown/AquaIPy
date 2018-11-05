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
#
"""This modules contains all the errors that are part of AquaIPy."""


class Error(Exception):
    """Base class for exceptions in this class."""

    pass


class ConnError(Error):
    """Raised when there is a connection error for an AI light.

    :ivar message: error message
    :ivar host: host
    """

    def __init__(self, message, host):
        """Initialise ConnError."""
        super().__init__()
        self.message = message
        self.host = host


class FirmwareError(Error):
    """Raised when connecting to a device that has unsupported firmware.

    :ivar message: error message
    :ivar firmware_version: unsupported version of firmware
    """

    def __init__(self, message, firmware_version):
        """Initialise FirmwareError."""
        super().__init__()
        self.message = message
        self.firmware_version = firmware_version


class MustBeParentError(Error):
    """Raised when connecting to a light that isn't the parent.

    The ``AquaIPy`` library only supports connecting to a parent light. There
    is support for paired devices, as long as the parent is the device that is
    connected to.

    :ivar message: error message
    :ivar parent_identifier: an identifier for the parent device
    """

    def __init__(self, message, parent_identifier):
        """Initialise MustBeParentError."""
        super().__init__()
        self.message = message
        self.parent_identifier = parent_identifier
