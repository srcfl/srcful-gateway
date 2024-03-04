import random
import server.crypto.crypto as crypto
from server.message import Message
import time


class BlackBoard:
    """
    Blackboard class is the subject class of the observer pattern.
    It is responsible for maintaining the state of the system and notifying
    the observers when the state changes.
    """

    _inverters: "BlackBoard.Inverters"
    _start_time: int
    _rest_server_port: int
    _rest_server_ip: str
    _messages: list[Message]

    def __init__(self):
        self._inverters = BlackBoard.Inverters()
        self._start_time = self.time_ms()
        self._rest_server_port = 80
        self._rest_server_ip = "localhost"

    def add_error(self, message: str):
        self._messages.append(Message(message, Message.Type.Error, self.time_ms() // 1_000, self._getMessageId()))

    def add_warning(self, message: str):
        self._messages.append(Message(message, Message.Type.Warning, self.time_ms() // 1_000, self._getMessageId()))

    def add_info(self, message: str):
        self._messages.append(Message(message, Message.Type.Info, self.time_ms() // 1_000, self._getMessageId()))

    def clear_messages(self):
        self._messages = []
    
    def delete_message(self, id):
        for m in self._messages:
            if m.id == id:
                self._messages.remove(m)
                return True
        return False

    def get_messages(self):
        return self._messages
    
    def _getMessageId(self):
        id = random.randint(0, 1000)
        def is_unique(id):
            for m in self._messages:
                if m.id == id:
                    return False
            return True
        while not is_unique(id):
            id = random.randint(0, 1000)
        return id

    
    @property
    def rest_server_port(self):
        return self._rest_server_port

    @rest_server_port.setter
    def rest_server_port(self, port:int):
        self._rest_server_port = port

    @property
    def rest_server_ip(self):
        return self._rest_server_ip

    @rest_server_ip.setter
    def rest_server_ip(self, ip:str):
        self._rest_server_ip = ip

    @property
    def inverters(self):
        return self._inverters

    @property
    def start_time(self):
        return self._start_time

    def get_version(self) -> str:
        return "0.7.0"

    def get_chip_info(self):
        crypto.init_chip()

        device_name = crypto.get_device_name()
        serial_number = crypto.get_serial_number().hex()

        crypto.release()

        return "device: " + device_name + " serial: " + serial_number

    def time_ms(self):
        return time.time_ns() // 1_000_000

    class Inverters:
        """Observable list of inverters"""

        def __init__(self):
            self.lst = []
            self._observers = set()

        def add_listener(self, observer):
            self._observers.add(observer)

        def remove_listener(self, observer):
            self._observers.remove(observer)

        def add(self, inverter):
            self.lst.append(inverter)
            for o in self._observers:
                o.add_inverter(inverter)

        def remove(self, inverter):
            if inverter in self.lst:
                self.lst.remove(inverter)
                for o in self._observers:
                    o.remove_inverter(inverter)
