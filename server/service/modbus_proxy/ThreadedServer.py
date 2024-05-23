import logging
import socket
import threading
import queue
import time

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)


class ThreadedServer(threading.Thread):
    def __init__(self, listen_host: str, listen_port: int, target_host: str, target_port: int):
        super().__init__(daemon=True)
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.target_host = target_host
        self.target_port = target_port

        # High-priority and normal-priority queues
        self.high_priority_queue = queue.Queue()
        self.normal_priority_queue = queue.Queue()
        self.trans_to_client = {}  # Map transaction IDs to the client sockets

        self.running = threading.Event()
        self.running.set()
        
        self.threads = []  # To keep track of all client threads

    def run(self):
        try:
            # Setup server socket with reuse address option
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.listen_host, self.listen_port))
            self.server_socket.listen(5)

            # Setup single persistent connection to the target device
            self.device_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.device_socket.connect((self.target_host, self.target_port))

            # Start handling requests in separate thread
            process_thread = threading.Thread(target=self._process_requests, daemon=True)
            process_thread.start()
            self.threads.append(process_thread)

            self._handle_connections()
        
        except Exception as e:
            log.error(f"Error in ModbusProxyServer: {e}")
            self.shutdown()

        # Wait for all threads to complete
        for thread in self.threads:
            thread.join()

    def _handle_connections(self):
        while self.running.is_set():
            try:
                client_socket, client_address = self.server_socket.accept()
                log.debug(f"New connection from {client_address}")
                client_thread = threading.Thread(target=self._handle_client, args=(client_socket, client_address), daemon=True)
                client_thread.start()
                self.threads.append(client_thread)
            except socket.timeout:
                continue
            except Exception as e:
                if self.running.is_set():
                    log.error(f"Error accepting connections: {e}")

    def _handle_client(self, client_socket, client_address):
        try:
            while self.running.is_set():
                data = client_socket.recv(1024)
                if data:
                    transaction_id = int.from_bytes(data[0:2], byteorder='big')
                    if client_address[0] == '127.0.0.1':
                        log.debug("Enqueueing high priority data from client %s : %s", client_address, data.hex())
                        self.high_priority_queue.put((client_socket, data, transaction_id))
                    else:
                        log.debug("Enqueueing normal priority data from client %s : %s", client_address, data.hex())
                        self.normal_priority_queue.put((client_socket, data, transaction_id))
                else:
                    log.debug("Connection closed by client %s", client_address)
                    self._close_socket(client_socket)
                    break
        except Exception as e:
            log.error("Error handling client %s : %s", client_address, e)
            self._close_socket(client_socket)

    def _process_requests(self):
        while self.running.is_set():
            try:
                if not self.high_priority_queue.empty():
                    client_socket, data, transaction_id = self.high_priority_queue.get_nowait()
                elif not self.normal_priority_queue.empty():
                    client_socket, data, transaction_id = self.normal_priority_queue.get_nowait()
                else:
                    time.sleep(0.01)
                    continue

                log.debug("Processing request with transaction ID: %s", transaction_id)
                self.trans_to_client[transaction_id] = client_socket
                self.device_socket.send(data)
                self._handle_device_response(transaction_id)
            except queue.Empty:
                time.sleep(0.01)
            except Exception as e:
                log.error("Error processing request: %s", e)

    def _handle_device_response(self, transaction_id):
        try:
            data = self.device_socket.recv(1024)
            if data:
                log.debug("Received data from device: %s", data.hex())
                tid = int.from_bytes(data[0:2], byteorder='big')
                client_socket = self.trans_to_client.pop(tid, None)
                if client_socket:
                    log.debug("Sending response to client %s : %s", client_socket.getpeername()[0], data.hex())
                    client_socket.send(data)
                else:
                    log.error("No client mapped to transaction ID %s", tid)
        except Exception as e:
            log.error("Error handling device response for transaction ID %s: %s", transaction_id, e)

    def _close_socket(self, s):
        log.debug("Closing socket %s", s)
        try:
            s.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass  # Socket was already closed or not connected
        s.close()

    def shutdown(self):
        log.info("Shutting down the proxy server gracefully")
        if self.running.is_set():
            self.running.clear()
            if self.server_socket:
                self._close_socket(self.server_socket)
            if self.device_socket:
                self._close_socket(self.device_socket)