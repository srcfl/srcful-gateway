import dbus
from constants import g_request_char_uuid, g_response_char_uuid, g_api_url
from cputemp.service import Application, Service, Characteristic, Descriptor
import egwttp
import logging
import requests

USER_DESC_DESCRIPTOR_UUID = "2901"
PRESENTATION_FORMAT_DESCRIPTOR_UUID = "2904"

logger = logging.getLogger(name=__name__)

class UTF8FormatDescriptor(Descriptor):

    def __init__(self, characteristic):
        Descriptor.__init__(self, PRESENTATION_FORMAT_DESCRIPTOR_UUID, ["read"], characteristic)

    def ReadValue(self, options):
        value = []
        value.append(dbus.Byte(0x19))
        value.append(dbus.Byte(0x00))
        value.append(dbus.Byte(0x00))
        value.append(dbus.Byte(0x00))
        value.append(dbus.Byte(0x01))
        value.append(dbus.Byte(0x00))
        value.append(dbus.Byte(0x00))

        return value


class LabelDescriptor(Descriptor):

    def __init__(self, characteristic, label):
        self.label = label
        Descriptor.__init__(self, USER_DESC_DESCRIPTOR_UUID, ["read"], characteristic)

    def ReadValue(self, options):
        return string_to_dbus_encoded_byte_array(self.label)



def string_to_dbus_encoded_byte_array(str):
    byte_array = []    
    for c in str:
        byte_array.append(dbus.Byte(c.encode()))

    return byte_array


def handle_response(path:str, reply: requests.Response):
  egwttp_response = egwttp.construct_response(path, reply.text)
  logger.debug(f"Reply: {egwttp_response}")
  return egwttp_response

def request_get(path: str) -> bytearray:
  return handle_response(path, requests.get(g_api_url + path))

def request_post(path: str, content: str) -> bytearray:
  return handle_response(path, requests.post(g_api_url + path, data=content))

class RequestChar(Characteristic):
    def __init__(self, service:Service, response):
        super().__init__(g_request_char_uuid, ["write"], service)
        self.responseChar = response
        self.count = 0
        self.add_descriptor(LabelDescriptor(self, "EGWTTP Request"))
        self.add_descriptor(UTF8FormatDescriptor(self))



    def WriteValue(self, value, options):
        self.count += 1
        self.responseChar.notifyValue = string_to_dbus_encoded_byte_array("Hello ble World %d" % self.count)
        #logger.debug('WriteValue: %s', value)

        str_val = bytes(value).decode('utf-8')
        

        if egwttp.is_request(str_val):
            logger.debug(f"Request received... {str_val}")
            header, content = egwttp.parse_request(str_val)

            if header['method'] == 'GET' or header['method'] == 'POST':
                response = request_get(header['path']) if header['method'] == 'GET' else request_post(header['path'], content)
                self.responseChar.notifyValue = string_to_dbus_encoded_byte_array(response)
            else:
                logger.debug("Not a GET or POST request, doing nothing")
        else:
            logger.debug("Not a EGWTTP request, doing nothing")
            
        self.responseChar.PropertiesChanged("org.bluez.GattCharacteristic1", {"Value": self.responseChar.notifyValue}, [])
        

class ResponseChar(Characteristic):

    def __init__(self, service:Service):
        self.notifyValue = string_to_dbus_encoded_byte_array("Hello ble World")
        super().__init__(g_response_char_uuid, ["read", "notify"], service)

        self.add_descriptor(LabelDescriptor(self, "EGWTTP Response"))
        self.add_descriptor(UTF8FormatDescriptor(self))

    def ReadValue(self, options):
        if "offset" in options:
            cutDownArray = self.notifyValue[int(options["offset"]):]
            return cutDownArray
        else:
            return self.notifyValue

        return 
    
    def StartNotify(self):
        logger.debug('Notify EGWTTP Responses')

    def StopNotify(self):
        logger.debug('Stop Notify EGWTTP Responses')

