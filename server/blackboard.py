import random
import time
import server.crypto.crypto as crypto
from server.message import Message
from server.tasks.itask import ITask

import logging

logger = logging.getLogger(__name__)


class BlackBoard:
    """
    Blackboard class is the publisher class of the observer pattern.
    It is responsible for maintaining the state of the system and notifying
    the observers when the state changes.
    It also acts as a repository for messages, and created tasks.
    Tasks can be added to the blackboard and will be executed by the main loop. This makes it possible for non Task objects to create tasks.
    """

    _inverters: "BlackBoard.Inverters"
    _start_time: int
    _rest_server_port: int
    _rest_server_ip: str
    _messages: list[Message]
    _tasks: list[ITask]

    def __init__(self):
        self._inverters = BlackBoard.Inverters()
        self._start_time = time.monotonic_ns()
        self._rest_server_port = 80
        self._rest_server_ip = "localhost"
        self._messages = []
        self._tasks = []

    def add_task(self, task: ITask):
        self._tasks.append(task)
    
    def purge_tasks(self):
        tasks = self._tasks
        self._tasks = []
        return tasks

    def add_error(self, message: str) -> Message:
        return self._add_message(Message(message, Message.Type.Error, self.time_ms() // 1_000, self._get_message_id()))

    def add_warning(self, message: str) -> Message:
        return self._add_message(Message(message, Message.Type.Warning, self.time_ms() // 1_000, self._get_message_id()))

    def add_info(self, message: str) -> Message:
        return self._add_message(Message(message, Message.Type.Info, self.time_ms() // 1_000, self._get_message_id()))

    def clear_messages(self):
        self._messages = []
    
    def delete_message(self, message_id: int):
        for m in self._messages:
            if m.id == message_id:
                self._messages.remove(m)
                return True
        return False

    @property
    def messages(self) -> tuple[Message]:
        return tuple(self._messages)
    
    def _add_message(self, message: Message) -> Message:
        # check if we already have a message then just update the timestamp and move to the last place in the list
        for m in self._messages:
            if m.message == message.message:
                m.timestamp = message.timestamp
                self._messages.remove(m)
                self._messages.append(m)

                return m
        # make sure we have a max of 10 messages
        self._messages.append(message)
        if len(self._messages) > 10:
            self._messages.pop(0)
        
        return message
    
    def _get_message_id(self):
        message_id = random.randint(0, 1000)

        def is_unique(message_id: int):
            for m in self._messages:
                if m.id == message_id:
                    return False
            return True
        while not is_unique(message_id):
            message_id = random.randint(0, 1000)
        return message_id

    
    @property
    def rest_server_port(self):
        return self._rest_server_port

    @rest_server_port.setter
    def rest_server_port(self, port: int):
        self._rest_server_port = port

    @property
    def rest_server_ip(self):
        return self._rest_server_ip

    @rest_server_ip.setter
    def rest_server_ip(self, ip: str):
        self._rest_server_ip = ip

    @property
    def inverters(self):
        return self._inverters

    @property
    def elapsed_time(self):
        return (time.monotonic_ns() - self._start_time) // 1_000_000

    def get_version(self) -> str:
        return "0.8.4"

    def get_chip_info(self):
        with crypto.Chip() as chip:
            device_name = chip.get_device_name()
            serial_number = chip.get_serial_number().hex()

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


