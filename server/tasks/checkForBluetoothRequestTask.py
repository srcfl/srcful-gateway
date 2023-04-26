import socket
import select
import logging

from threading import Thread

from .task import Task
from bluetooth import *


log = logging.getLogger(__name__)

# inspo from: https://github.com/gitdefllo/lighthouse-weather-station/blob/feature_classic_bluetooth/station/main_lighthouse.py
# pip install git+https://github.com/pybluez/pybluez.git#egg=pybluez - on windows at least

class CheckForBluetoothRequest(Task):
  def __init__(self, eventTime: int, stats: dict, ):
    super().__init__(eventTime, stats)
    if not 'btRequests' in self.stats:
      self.stats['btRequests'] = 0

    server_sock = BluetoothSocket(RFCOMM)
    server_sock.bind(("", PORT_ANY))
    server_sock.listen(1)
    port = server_sock.getsockname()[1]
    uuid = '6a8f42ea-2262-41f4-b128-7112f2173ede'
    advertise_service(server_sock, 'SrcFul Energy Gatway Service', service_id=uuid,
                      service_classes=[uuid, SERIAL_PORT_CLASS], profiles=[SERIAL_PORT_PROFILE])

    self.server_sock = server_sock
    self.server_sock.setblocking(False)

    self.sockets = [server_sock]
    self.clients = {}
    log.info("Waiting for bluetooth connection on RFCOMM channel {}".format(port))

  def __del__(self):
    
    stop_advertising(self.server_sock)
    self.server_sock.close()

  def _close_client(self, client_sock: socket):
    assert (client_sock in self.clients)
    log.info("Closing bluetooth connection from {}".format(
        self.clients[client_sock]))
    client_sock.close()
    self.sockets.remove(client_sock)
    del self.clients[client_sock]

  def execute(self, eventTime: int) -> None|Task|list[Task]:
    read_sockets, write_sockets, exeption_sockets = select.select(self.sockets, self.sockets, self.sockets, 0)

    for sock in read_sockets:
      if sock == self.server_sock:
        client_sock, address = self.server_sock.accept()
        client_sock.setblocking(False)
        self.sockets.append(client_sock)
        self.clients[client_sock] = address
        log.info("Accepted bluetooth connection from {}".format(address))
      else:
        data = sock.recv(1024)
        if data:
          log.info("Received bluetooth data from {}: {}".format(self.clients[sock], data))
          # TODO: continue reading more data if needed and then finally send response
          # Maybe we need a separate class to handle this for each socket.
          # eg. this will be our application level protocol and maybe we can use http
          sock.send(data)
        else:
          log.info("Closing bluetooth connection from {}".format(self.clients[sock]))
          sock.close()
          self.sockets.remove(sock)
          del self.clients[sock]

    for sock in exeption_sockets:
      self._close_client(sock)
    
    self.time = eventTime + 25
    return self
