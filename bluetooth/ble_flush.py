#!/usr/bin/python3

# This script removes any devices that cannot be reconnected to
# this is useful when a paried device has removed the paring on its side and we are still paired
# in this situation the device must be removed before it can be re-paired

from __future__ import absolute_import, print_function, unicode_literals
import argparse
from gi.repository import GLib

import os
import sys
import time
import dbus
import dbus.service
import dbus.mainloop.glib

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
RECONNECT_MAX_RETRIES = os.getenv("RECONNECT_MAX_RETRIES", 7)

# DBus helper functions
def dbus_get_interface(bus, bus_name, object_name, interface_name):
    dbus_obj = bus.get_object(bus_name, object_name)
    return dbus.Interface(dbus_obj, interface_name)

def dbus_set_property(bus, bus_name, object_name, interface_name, prop_name, value):
    props = dbus_get_interface(bus, bus_name, object_name, DBUS_INTERFACE_PROPERTIES)
    props.Set(interface_name, prop_name, value)

def dbus_get_property(bus, bus_name, object_name, interface_name, prop_name):
    props = dbus_get_interface(bus, bus_name, object_name, DBUS_INTERFACE_PROPERTIES)
    return props.Get(interface_name, prop_name)

def dbus_get_all_properties(bus, bus_name, object_name, interface_name):
  props = dbus_get_interface(bus, bus_name, object_name, DBUS_INTERFACE_PROPERTIES)
  return props.GetAll(interface_name)

def dbus_filter_objects_by_interface(objects, interface_name):
    result = []
    for path in objects.keys():
        interfaces = objects[path]
        for interface in interfaces.keys():
            if interface == interface_name:
                result.append(path)
    return result



def remove_all_paired_devices():
    # Initialize DBus library
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()

    # Set agent settings
    interface = DEFAULT_INTERFACE

    # Set bluez discoverable timeout to infinite. Most smartphones won't connect with shorter timeouts
    dbus_set_property(bus, DBUS_NAME, DBUS_OBJECT + '/' + interface, DBUS_INTERFACE_ADAPTER, "DiscoverableTimeout", dbus.UInt32(0))


    # Reestablish connection with previously connected devices
    bluez_manager = dbus_get_interface(bus, "org.bluez", "/", "org.freedesktop.DBus.ObjectManager")
    bluez_objects = bluez_manager.GetManagedObjects()
    device_paths = dbus_filter_objects_by_interface(bluez_objects, "org.bluez.Device1")
    adapter = dbus_get_interface(bus, "org.bluez", DBUS_OBJECT + '/' + interface, "org.bluez.Adapter1")

    # it seems very flaky to reconnect to devices this way for some reason

    print("Checking for known bluetooth devices...")
    for device_path in device_paths:
        props = dbus_get_all_properties(bus, "org.bluez", device_path, "org.bluez.Device1")
        #print("checking.... - %s (%s)..." % (props["Name"], props["Address"]))
        #print(props)
        if bool(props["Paired"]):
            print("- Removing %s (%s)..." % (props["Name"], props["Address"]))

            # Try to reconnect...
            # Bluez throws "Protocol not available" if the host device is not ready to accept the target device profile reconnection request
            # Since the bluetooth block is not responsible for bluetooth profile's acceptance (for instance audio block is for A2DP profiles)
            # we introduce a delay and retry a few times before assuming it's not possible to reconnect.
            device = dbus_get_interface(bus, "org.bluez", device_path, "org.bluez.Device1")
            adapter.RemoveDevice(device)
    print("Done.")