import logging
import socket
import select
from server.blackboard import BlackBoard
from .task import Task
import time

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

class ModbusProxyTask(Task):
    def __init__(self, event_time: int, bb: BlackBoard, listen_host: str, listen_port: int, target_host: str, target_port: int):
        super().__init__(event_time, bb)
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.target_host = target_host
        self.target_port = target_port

        # Setup server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.listen_host, self.listen_port))
        self.server_socket.listen(5)
        self.server_socket.setblocking(False)  # Set non-blocking mode

        # List of sockets to monitor
        self.inputs = [self.server_socket]
        self.outputs = []
        self.client_to_device = {}  # Map client sockets to device sockets
        self.device_to_client = {}  # Map device sockets to client sockets
        
    def execute(self, event_time):
        readable, writable, exceptional = select.select(self.inputs, self.outputs, self.inputs, 0.01)

        for s in readable:
            if s is self.server_socket:
                client_socket, client_address = s.accept()
                log.debug(f"New connection from {client_address}")
                client_socket.setblocking(False)
                self.inputs.append(client_socket)
                try:
                    device_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    device_socket.connect((self.target_host, self.target_port))
                    device_socket.setblocking(False)
                    self.inputs.append(device_socket)
                    self.client_to_device[client_socket] = device_socket
                    self.device_to_client[device_socket] = client_socket
                except Exception as e:
                    log.error(f"Could not connect to target device: {e}")
                    self._close_socket(client_socket)
            else:
                try:
                    data = s.recv(1024)
                    if data:
                        if s in self.client_to_device:
                            #log.debug(f"Forwarding data from client to target device: {data.hex()}")
                            device_socket = self.client_to_device[s]
                            device_socket.send(data)
                        elif s in self.device_to_client:
                            #log.debug(f"Forwarding data from target device to client: {data.hex()}")
                            client_socket = self.device_to_client[s]
                            client_socket.send(data)
                    else:
                        self._close_socket(s)
                except Exception as e:
                    self._close_socket(s)
                    log.error(f"Error handling data: {e}")

        for s in exceptional:
            self._close_socket(s)

        self.adjust_time(self.bb.time_ms() + 25)
        return self

    def _close_socket(self, s):
        log.debug(f"Closing socket {s}")
        if s in self.inputs:
            self.inputs.remove(s)
        if s in self.outputs:
            self.outputs.remove(s)
        if s in self.client_to_device:
            device_socket = self.client_to_device[s]
            if device_socket in self.inputs:
                self.inputs.remove(device_socket)
            if device_socket in self.outputs:
                self.outputs.remove(device_socket)
            device_socket.close()
            del self.device_to_client[device_socket]
            del self.client_to_device[s]
        if s in self.device_to_client:
            client_socket = self.device_to_client[s]
            if client_socket in self.inputs:
                self.inputs.remove(client_socket)
            if client_socket in self.outputs:
                self.outputs.remove(client_socket)
            client_socket.close()
            del self.client_to_device[client_socket]
            del self.device_to_client[s]
        s.close()