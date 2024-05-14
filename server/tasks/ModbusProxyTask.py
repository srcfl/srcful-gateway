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

        # Setup single persistent connection to the target device
        self.device_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.device_socket.connect((self.target_host, self.target_port))
        self.device_socket.setblocking(False)

        # List of sockets to monitor
        self.inputs = [self.server_socket, self.device_socket]
        self.outputs = []
        self.client_to_device = {}  # Map client sockets to data buffers

    def execute(self, event_time):
        readable, writable, exceptional = select.select(self.inputs, self.outputs, self.inputs, 0.01)

        for s in readable:
            if s is self.server_socket:
                client_socket, client_address = s.accept()
                log.debug(f"New connection from {client_address}")
                client_socket.setblocking(False)
                self.inputs.append(client_socket)
                self.client_to_device[client_socket] = b''
            elif s is self.device_socket:
                try:
                    data = self._read_modbus(s)
                    if data:
                        log.debug(f"Forwarding data from device to client: {data.hex()}")
                        for client_socket, client_data in self.client_to_device.items():
                            client_socket.send(data)
                    else:
                        log.error("Device connection closed unexpectedly")
                        self._close_socket(s)
                except Exception as e:
                    log.error(f"Error receiving data from device: {e}")
            else:
                try:
                    data = self._read_modbus(s)
                    if data:
                        log.debug(f"Forwarding data from client to target device: {data.hex()}")
                        self.device_socket.send(data)
                    else:
                        self._close_socket(s)
                except Exception as e:
                    self._close_socket(s)
                    log.error(f"Error handling data from client: {e}")

        for s in exceptional:
            self._close_socket(s)

        self.adjust_time(event_time + 25)
        return self

    def _read_modbus(self, s):
        header = s.recv(6)
        if len(header) < 6:
            return None
        size = int.from_bytes(header[4:], "big")
        transaction_id = int.from_bytes(header[:2], "big")
        log.debug(f"Reading {size} bytes from {s}")
        reply = header + s.recv(size)
        return reply

    def _close_socket(self, s):
        log.debug(f"Closing socket {s}")
        if s in self.inputs:
            self.inputs.remove(s)
        if s in self.outputs:
            self.outputs.remove(s)
        if s in self.client_to_device:
            del self.client_to_device[s]
        s.close()

        # 007b 00000007 01030406a3b229
        # 007c 00000006 01039ca40002