import asyncio
import logging

from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
)


from pymodbus import pymodbus_apply_logging_config
from pymodbus.server import ModbusTcpServer


class Event_ts(asyncio.Event):

    def set(self):
        # FIXME: The _loop attribute is not documented as public api!
        self._loop.call_soon_threadsafe(super().set)


_STOP_EVENT: Event_ts = None
_SHOULD_REPLY: bool = True

_logger = logging.getLogger(__name__)


class Manipulator:
    """A Class to run the server.

    Using a class allows the easy use of global variables, but
    are not strictly needed
    """

    def __init__(self, port: int):
        self.port = port
        self.message_count = 3
        self.server = None
        self.context = None

    port: int = 5021
    message_count: int = 3
    server: ModbusTcpServer = None
    context: ModbusServerContext = None

    def server_request_tracer(self, request, *_addr):
        """Trace requests.

        All server requests passes this filter before being handled.
        """
        print(f"---> REQUEST: {request}")

    def server_response_manipulator(self, response):
        """Manipulate responses.

        All server responses passes this filter before being sent.
        The filter returns:

        - response, either original or modified
        - skip_encoding, signals whether or not to encode the response
        """

        #print(f"---> RESPONSE: {response}")
        self.message_count -= 1

        if not _SHOULD_REPLY:
            print("---> NOT RESPONDING!")
            response.should_respond = False

        return response, False

    async def setup(self):
        """Prepare server."""
        pymodbus_apply_logging_config(logging.INFO)
        datablock = ModbusSequentialDataBlock(40000, [17] * 200)    # this should cover sungrow inverter
        self.context = ModbusServerContext(
            slaves=ModbusSlaveContext(
                di=datablock, co=datablock, hr=datablock, ir=datablock
            ),
            single=True,
        )
        self.server = ModbusTcpServer(
            self.context,
            identity=None,
            address=("127.0.0.1", self.port),
            request_tracer=self.server_request_tracer,
            response_manipulator=self.server_response_manipulator,
        )

    async def run(self):
        """Attach Run server."""
        await self.server.serve_forever()


async def updating_task(server: Manipulator):
    """Update values in server.

    This task runs continuously beside the server
    It will increment some values each two seconds.

    It should be noted that getValues and setValues are not safe
    against concurrent use.
    """
    fc_as_hex = 3
    slave_id = 0x00
    address = 40000
    count = 6

    # set values to zero
    #values = server.context[slave_id].getValues(fc_as_hex, address, count=count)
    #values = [0 for v in values]
    #server.context[slave_id].setValues(fc_as_hex, address, values)

    #txt = (
    #    f"updating_task: started: initialised values: {values!s} at address {address!s}"
    #)
    #print(txt)
    #_logger.debug(txt)

    print("updating_task: started")

    global _STOP_EVENT
    _STOP_EVENT = Event_ts()

    # incrementing loop
    while True:
        await _STOP_EVENT.wait()
        print("Shutting down server...")
        await server.server.shutdown()
        _STOP_EVENT.clear()

        #print(f"Message count at {server.message_count}")
        # if server.message_count < 1:
        #    print("Shutting down server...")
        #    await server.server.shutdown()

        # values = context[slave_id].getValues(fc_as_hex, address, count=count)
        # values = [v + 1 for v in values]
        # context[slave_id].setValues(fc_as_hex, address, values)

        # txt = f"updating_task: incremented values: {values!s} at address {address!s}"
        # print(txt)
        # _logger.debug(txt)


async def run_updating_server(server):
    """Internal Start updating_task concurrently with the current task."""

    await server.setup()

    task = asyncio.create_task(updating_task(server))
    task.set_name("example updating task")

    await server.run()

    task.cancel()


async def main(server):
    """internal Combine setup and run."""
    print("Running server...")
    await run_updating_server(server)
    print("Server stopped... ")


def stop_server():
    """Call from outside to stop server."""
    _STOP_EVENT.set()


def start_server(port: int):
    """Call from outside to run server."""
    server = Manipulator(port)
    asyncio.run(main(server), debug=False)


def should_reply(do_reply: bool):
    """Call from outsdie to set whether the server should reply to requests."""
    global _SHOULD_REPLY
    _SHOULD_REPLY = do_reply

# if __name__ == "__main__":
#    start_server()
