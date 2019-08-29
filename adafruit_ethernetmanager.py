# The MIT License (MIT)
#
# Copyright (c) 2019 Brent Rubell for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`adafruit_ethernetmanager`
================================================================================

Ethernet hardware manager for CircuitPython


* Author(s): Brent Rubell

Implementation Notes
--------------------

**Hardware:**

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases
"""
import time
import wiznet
import socket

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_EthernetManager.git"


class Ethernet_Exception(Exception):
    """Exception raised on ethernet errors."""
    # pylint: disable=unnecessary-pass
    pass


class EthernetManager:
    """Class to assist manage interfacing with ethernet network hardware.

    TODO: Add docstrings for args
    """

    def __init__(self, spi, cs, reset_pin=None, status_pixel=None, debug=False):
        if reset_pin is not None:
            self.eth = wiznet.WIZNET5K(spi, cs, reset_pin)
        else:
            self.eth = wiznet.WIZNET5K(spi, cs)
        # TODO: Add requests.set_socket() impl here?
        # or set it in connect() with a successful connection...
        self.debug = debug
        self.statuspix = status_pixel
        self.pixel_status(0)

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.deinit()

    def deinit(self):
        """De-initializes ethernet interface.
        """
        self.eth = None

    def reset(self):
        raise NotImplementedError(
            "Reset pin must be provided to EthernetManager prior to initialization."
        )

    def connect(self, attempts=30):
        """Attempts connecting with ethernet using the current settings.
        Returns True if ethernet interface is connected.
        :param int attempts: Optional amount of connection failures before returning False.
        """
        failure_count = 0
        if self.is_connected:
            if self.debug:
                print("Checking for DCHP server...")
            self.pixel_status((100, 0, 0))
            while self.eth.ifconfig()[0] == "0.0.0.0":
                failure_count += 1
                if failure_count >= attempts:
                    return False
                time.sleep(1)
            self.pixel_status((0, 100, 0))
            return True
        else:
            raise Ethernet_Exception("Disconnected - plug an ethernet cable in.")

    def pixel_status(self, value):
        """
        Change Status Pixel if it was defined

        :param value: The value to set the Board's status LED to
        :type value: int or 3-value tuple
        """
        if self.statuspix:
            if hasattr(self.statuspix, "color"):
                self.statuspix.color = value
            else:
                self.statuspix.fill(value)

    def readline(self, sock):
        """Returns bytes up to '\r\n'"""
        line = bytes()
        while True:
            data = sock.recv(1)
            line +=data
            if not data or "\r\n" in line: break
        return line

    @property
    def is_connected(self):
        """Returns if an ethernet cable is physically connected."""
        return self.eth.connected

    @property
    def dchp(self):
        """Returns if DHCP is active."""
        return self.eth.dchp

    @dchp.setter
    def dchp(self, is_active):
        """Set to activate DCHP.
        :param bool is_active: Set True to activate DCHP.
        """
        self.eth.dchp = is_active
        return

    @property
    def ifconfig(self):
        """Returns a tuple consisting of the ip_address,
        subnet_mask, gateway_address, and the dns_server.
        """
        return self.eth.ifconfig

    @ifconfig.setter
    def ifconfig(self, ip_address, subnet_mask, gateway_address, dns_server):
        """Sets and configures the ethernet interface. Turns DCHP off, if it was on.
        :param str ip_address: Interface's ip address.
        :param str subnet_mask: Interface's subnet mask.
        :param str gateway_address: Interface's gateway address.
        :param str dns_server: Interface's dns server.
        """
        self.eth.ifconfig(ip_address, subnet_mask, gateway_address, dns_server)
        return

    @property
    def ip_address(self):
        """Returns the IP Address as a formatted string"""
        return self.ifconfig()[0]