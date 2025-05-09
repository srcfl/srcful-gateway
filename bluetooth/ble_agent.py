# Based on https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/test/simple-agent
# and https://github.com/nicokaiser/rpi-audio-receiver/blob/master/install-bluetooth.sh
from __future__ import absolute_import, print_function, unicode_literals
import argparse
import os
import dbus
import dbus.service
import dbus.mainloop.glib
import logging

logger = logging.getLogger(__name__)

# Bluez DBus constants
DBUS_NAME = "org.bluez"
DBUS_OBJECT = "/org/bluez"
DBUS_INTERFACE_PROPERTIES = "org.freedesktop.DBus.Properties"
DBUS_INTERFACE_AGENT = "org.bluez.Agent1"
DBUS_INTERFACE_MANAGER = "org.bluez.AgentManager1"
DBUS_INTERFACE_DEVICE = "org.bluez.Device1"
DBUS_INTERFACE_ADAPTER = "org.bluez.Adapter1"

# Agent default settings
capabilities = [ "KeyboardDisplay", "NoInputNoOutput" ]
DEFAULT_CAPABILITY = os.getenv("AGENT_CAPABILITY", "NoInputNoOutput")
DEFAULT_INTERFACE = os.getenv("HCI_INTERFACE", "hci0")
DEFAULT_PIN_CODE = os.getenv("PIN_CODE", "0000")

# Other settings
RECONNECT_MAX_RETRIES = os.getenv("RECONNECT_MAX_RETRIES", 5)

# DBus helper functions
def dbus_get_interface(bus_name, object_name, interface_name):
    dbus_obj = bus.get_object(bus_name, object_name)
    return dbus.Interface(dbus_obj, interface_name)

def dbus_set_property(bus_name, object_name, interface_name, prop_name, value):
    props = dbus_get_interface(bus_name, object_name, DBUS_INTERFACE_PROPERTIES)
    props.Set(interface_name, prop_name, value)

def dbus_get_property(bus_name, object_name, interface_name, prop_name):
    props = dbus_get_interface(bus_name, object_name, DBUS_INTERFACE_PROPERTIES)
    return props.Get(interface_name, prop_name)

def dbus_get_all_properties(bus_name, object_name, interface_name):
  props = dbus_get_interface(bus_name, object_name, DBUS_INTERFACE_PROPERTIES)
  return props.GetAll(interface_name)

def dbus_filter_objects_by_interface(objects, interface_name):
    result = []
    for path in objects.keys():
        interfaces = objects[path]
        for interface in interfaces.keys():
            if interface == interface_name:
                result.append(path)
    return result

def valid_pin_code(pin_code):
    try:
        int_pin_code = int(pin_code)
    except:
        return False
    return len(pin_code) > 0 and len(pin_code) <= 6 and int_pin_code >= 0 and int_pin_code <= 999999

class Agent(dbus.service.Object):
    exit_on_release = True

    def __init__(self, bus, path, pin_code):
        self.pin_code = pin_code
        super(Agent, self).__init__(bus, path)

    def set_exit_on_release(self, exit_on_release):
        self.exit_on_release = exit_on_release

    @dbus.service.method(DBUS_INTERFACE_AGENT, in_signature="", out_signature="")
    def Release(self):
        logger.info("Release")
        if self.exit_on_release:
            mainloop.quit()

    @dbus.service.method(DBUS_INTERFACE_AGENT, in_signature="os", out_signature="")
    def AuthorizeService(self, device, uuid):
        logger.info("AuthorizeService (%s, %s)", device, uuid)
        dbus_set_property(DBUS_NAME, device, DBUS_INTERFACE_DEVICE, "Trusted", True)
        return

    @dbus.service.method(DBUS_INTERFACE_AGENT, in_signature="o", out_signature="s")
    def RequestPinCode(self, device):
        logger.info("RequestPinCode (%s)", device)
        dbus_set_property(DBUS_NAME, device, DBUS_INTERFACE_DEVICE, "Trusted", True)
        return self.pin_code

    @dbus.service.method(DBUS_INTERFACE_AGENT, in_signature="o", out_signature="u")
    def RequestPasskey(self, device):
        logger.info("RequestPasskey (%s)", device)
        dbus_set_property(DBUS_NAME, device, DBUS_INTERFACE_DEVICE, "Trusted", True)
        return dbus.UInt32(PIN_CODE)

    @dbus.service.method(DBUS_INTERFACE_AGENT, in_signature="ouq", out_signature="")
    def DisplayPasskey(self, device, passkey, entered):
        logger.info("DisplayPasskey (%s, %06u entered %u)",  device, passkey, entered)

    @dbus.service.method(DBUS_INTERFACE_AGENT, in_signature="os", out_signature="")
    def DisplayPinCode(self, device, pincode):
        logger.info("DisplayPinCode (%s, %s)", device, pincode)

    @dbus.service.method(DBUS_INTERFACE_AGENT, in_signature="ou", out_signature="")
    def RequestConfirmation(self, device, passkey):
        logger.info("RequestConfirmation (%s, %06d)", device, passkey)
        dbus_set_property(DBUS_NAME, device, DBUS_INTERFACE_DEVICE, "Trusted", True)
        return

    @dbus.service.method(DBUS_INTERFACE_AGENT, in_signature="o", out_signature="")
    def RequestAuthorization(self, device):
        logger.info("RequestAuthorization (%s)", device)
        dbus_set_property(DBUS_NAME, device, DBUS_INTERFACE_DEVICE, "Trusted", True)
        return

    @dbus.service.method(DBUS_INTERFACE_AGENT, in_signature="", out_signature="")
    def Cancel(self):
        logger.info("Cancel")

if __name__ == "__main__":
    # Initialize DBus library
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()

    # Parse command line options
    parser = argparse.ArgumentParser(description='Balena bluez authentication agent')
    parser.add_argument("-c", "--capability", dest="capability", choices=capabilities, default=DEFAULT_CAPABILITY, help="Define the bluez agent capability. Defaults to 'NoInputNoOutput'.")
    parser.add_argument("-i", "--interface", dest="interface", default=DEFAULT_INTERFACE, help="Define the bluetooth interface to be used. Defaults to 'hci0'.")
    parser.add_argument("-p", "--pincode", dest="pin_code", default=DEFAULT_PIN_CODE, help="Set PIN Code to be used for authentication. Only used if running in legacy mode (SSP off). Defaults to '0000'")
    args = parser.parse_args()

    # Set agent settings
    capability = args.capability or DEFAULT_CAPABILITY
    interface = args.interface or DEFAULT_INTERFACE
    pin_code = args.pin_code if valid_pin_code(args.pin_code) else DEFAULT_PIN_CODE

    # Set bluez discoverable timeout to infinite. Most smartphones won't connect with shorter timeouts
    dbus_set_property(DBUS_NAME, DBUS_OBJECT + '/' + interface, DBUS_INTERFACE_ADAPTER, "DiscoverableTimeout", dbus.UInt32(0))

    # Create and register bluetooth agent
    path = "/test/agent"
    agent = Agent(bus, path, pin_code)
    manager = dbus_get_interface(DBUS_NAME, DBUS_OBJECT, DBUS_INTERFACE_MANAGER)
    manager.RegisterAgent(path, capability)
    manager.RequestDefaultAgent(path)

    # Log agent info
    logger.info("Bluetooth agent started!")