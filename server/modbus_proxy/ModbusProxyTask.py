import logging
import socket
import select
from server.blackboard import BlackBoard
from ..tasks.task import Task

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
        self.trans_to_client = {}  # Map transaction IDs to the client sockets

    def execute(self, event_time):
        readable, writable, exceptional = select.select(self.inputs, self.outputs, self.inputs, 0.01)

        for s in readable:
            if s is self.server_socket:
                client_socket, client_address = s.accept()
                log.debug(f"New connection from {client_address}")
                client_socket.setblocking(False)
                self.inputs.append(client_socket)
            elif s is self.device_socket:
                # Handle responses from the target device
                try:
                    data, transaction_id = self._read_modbus(s)
                    if data:
                        # log.debug(f"Forwarding data from device to client: {data.hex()}")
                        client_socket = self.trans_to_client.pop(transaction_id, None)
                        if client_socket:
                            client_socket.send(data)
                        else:
                            log.error(f"Transaction ID {transaction_id} not found in map")
                    else:
                        # log.error("Device connection closed unexpectedly")
                        self._close_socket(s)
                except Exception as e:
                    log.error(f"Error receiving data from device: {e}")
            else:
                # Handle requests from clients
                try:
                    data, transaction_id = self._read_modbus(s)
                    if data:
                        # log.debug(f"Forwarding data from client to target device: {data.hex()}")
                        self.trans_to_client[transaction_id] = s
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
        # Read the header
        header = s.recv(6)
        if len(header) < 6:
            return None, None
        
        # Extract the transaction ID and the size of the remaining frame
        transaction_id = int.from_bytes(header[0:2], byteorder='big')
        length = int.from_bytes(header[4:6], byteorder='big')
        
        if length < 1:
            return None, None

        # Read the remaining part of the frame
        remainder = s.recv(length)
        frame = header + remainder
        # log.debug(f"Received frame: {frame.hex()} with transaction ID: {transaction_id}")
        return frame, transaction_id

    def _close_socket(self, s):
        log.debug(f"Closing socket {s}")
        if s in self.inputs:
            self.inputs.remove(s)
        if s in self.outputs:
            self.outputs.remove(s)
        if s in self.client_to_device:
            del self.client_to_device[s]
        trans_ids_to_remove = [tid for tid, cs in self.trans_to_client.items() if cs is s]
        for trans_id in trans_ids_to_remove:
            del self.trans_to_client[trans_id]
        s.close()

        # 007b 00000007 01030406a3b229
        # 007c 00000006 01039ca40002