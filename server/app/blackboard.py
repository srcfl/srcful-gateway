import random
import time
import logging
from server.app.isystem_time import ISystemTime
from server.app.itask_source import ITaskSource
import server.crypto.crypto as crypto
from server.app.message import Message
from server.crypto.crypto_state import CryptoState
from server.tasks.itask import ITask
from server.app.settings import Settings, ChangeSource
from server.devices.ICom import ICom

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class BlackBoard(ISystemTime, ITaskSource):
    """
    Blackboard class is the publisher class of the observer pattern.
    It is responsible for maintaining the state of the system and notifying
    the observers when the state changes.
    It also acts as a repository for messages, and created tasks.
    Tasks can be added to the blackboard and will be executed by the main loop. This makes it possible for non Task objects to create tasks.
    """

    _devices: "BlackBoard.Devices"
    _start_time: int
    _rest_server_port: int
    _rest_server_ip: str
    _messages: list[Message]
    _chip_death_count: int
    _settings: Settings
    _crypto_state: CryptoState
    _available_devices: list[ICom]
    _tasks: list[ITask]

    def __init__(self, crypto_state: CryptoState):
        self._tasks = []
        self._devices = BlackBoard.Devices()
        self._start_time = time.monotonic_ns()
        self._rest_server_port = 80
        self._rest_server_ip = "localhost"
        self._messages = []
        self._chip_death_count = 0
        self._settings = Settings()
        self._settings.harvest.add_endpoint("https://mainnet.srcful.dev/gw/data/", ChangeSource.LOCAL)
        self._crypto_state = crypto_state
        self._available_devices = []
        
    def get_version(self) -> str:
        return "0.17.1"
        
    def add_task(self, task: ITask):
        self._tasks.append(task)

    def purge_tasks(self) -> list[ITask]:
        ret = self._tasks
        self._tasks = []
        return ret
    
    def _save_state(self):
        from server.tasks.saveStateTask import SaveStateTask
        self.add_task(SaveStateTask(self.time_ms() + 100, self))

    def add_error(self, message: str) -> Message:
        ret = self._add_message(Message(message, Message.Type.Error, self.time_ms() // 1_000, self._get_message_id()))
        self._save_state()
        return ret

    def add_warning(self, message: str) -> Message:
        ret = self._add_message(Message(message, Message.Type.Warning, self.time_ms() // 1_000, self._get_message_id()))
        self._save_state()
        return ret

    def add_info(self, message: str) -> Message:
        ret = self._add_message(Message(message, Message.Type.Info, self.time_ms() // 1_000, self._get_message_id()))
        self._save_state()
        return ret

    def clear_messages(self):
        self._messages = []
        self._save_state()
    
    def delete_message(self, message_id: int):
        for m in self._messages:
            if m.id == message_id:
                self._messages.remove(m)
                self._save_state()
                return True
        return False
    
    @property
    def settings(self) -> Settings:
        return self._settings

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
    def state(self) -> dict:
        state = dict()
        state['status'] = {'version': self.get_version(), 'uptime': self.elapsed_time, 'messages': self.message_state()}
        state['timestamp'] = self.time_ms()
        state['crypto'] = self.crypto_state().to_dict(self.chip_death_count)
        state['network'] = self.network_state()
        state['devices'] = self.devices_state()
        state['available_devices'] = [device.get_config() for device in self.get_available_devices()]
        return state
    
    def message_state(self) -> dict:
        ret = []
        for m in self.messages:
            m_dict = {
                "message": m.message,
                "type": m.type.value,
                "timestamp": m.timestamp,
                "id": m.id
            }
            ret.append(m_dict)
        return ret

    def crypto_state(self) -> CryptoState:
        return self._crypto_state
    
    def network_state(self) -> dict:
        try:
            from server.network.scan import WifiScanner
            s = WifiScanner()
            ssids = s.get_ssids()

            from server.web.handler.get.network import AddressHandler
            address = AddressHandler().get(self.rest_server_port)

            return {"wifi": {"ssids": ssids}, "address": address}
        except Exception as e:
            logger.error(e)
            return {"error": str(e)}
    
    def devices_state(self) -> list[dict]:
        ret = {'configured': []}

        for device in self._devices.lst:
            device_state = {}
            device_state['connection'] = device.get_config()
            device_state['is_open'] = device.is_open()
            ret['configured'].append(device_state)

        import server.web.handler.get.supported as supported
        ret['supported'] = supported.Handler().get_supported_inverters()
        return ret
    
    def get_available_devices(self) -> list[ICom]:
        return self._available_devices
    
    def set_available_devices(self, devices: list[ICom]):
        self._available_devices = devices
        self._save_state()
    
    @property
    def chip_death_count(self):
        return self._chip_death_count

    def increment_chip_death_count(self):
        self._chip_death_count += 1

    def reset_chip_death_count(self):
        self._chip_death_count = 0

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
    def devices(self):
        return self._devices

    @property
    def elapsed_time(self):
        return (time.monotonic_ns() - self._start_time) // 1_000_000

    def get_chip_info(self):
        with crypto.Chip() as chip:
            device_name = chip.get_device_name()
            serial_number = chip.get_serial_number().hex()

        return "device: " + device_name + " serial: " + serial_number

    def time_ms(self):
        return time.time_ns() // 1_000_000

    class Devices:
        """Observable list of communication objects"""

        def __init__(self):
            self.lst = []
            self._observers = set()

        def add_listener(self, observer):
            self._observers.add(observer)

        def remove_listener(self, observer):
            self._observers.remove(observer)
            
        def contains(self, device: ICom) -> bool:
            return self.find_sn(device.get_SN()) is not None

        def find_sn(self, sn: str) -> ICom | None:
            for d in self.lst:
                if d.get_SN() == sn:
                    return d
            return None

        def add(self, device:ICom):
            assert device.is_open(), "Only open devices can be added to the blackboard"
            
            existing_device = self.find_sn(device.get_SN())
            if existing_device == device:
                return
            
            if existing_device:
                self.remove(existing_device)
            
            self.lst.append(device)
                
            for o in self._observers:
                o.add_device(device)

        def remove(self, device:ICom):
            if device in self.lst:
                self.lst.remove(device)
                for o in self._observers:
                    o.remove_device(device)
                    
                    


