import threading
import logging

from cputemp.bletools import BleTools
from cputemp.service import Application, Service, Characteristic, Descriptor
from constants import g_service_uuid, g_request_char_uuid, g_response_char_uuid

from BleAdv import BluetoothConnectionAdvertisement

from chars import RequestChar, ResponseChar


logger = logging.getLogger(name=__name__)
ADVERTISEMENT_TYPE = 'peripheral'
ADVERTISEMENT_INDEX = 0
ADVERTISEMENT_SECONDS = 3000
ADVERTISEMENT_OFF_SLEEP_SECONDS = 5

class BluetoothAdvertisementProcessor(Application):
    def __init__(self, eth0_mac_address, variant_details):
        super().__init__()

        self.connection_advertisement = BluetoothConnectionAdvertisement(
            ADVERTISEMENT_INDEX, eth0_mac_address,
            ADVERTISEMENT_TYPE, variant_details)
        self.stop_advertisement_timer = None

        egwTTPService = Service(0, g_service_uuid, True)

        
        response = ResponseChar(egwTTPService)
        request = RequestChar(egwTTPService, response)

        egwTTPService.add_characteristic(request)
        egwTTPService.add_characteristic(response)

        self.add_service(egwTTPService)


        self.register()

    def start_advertisement(self):
        logger.debug("Starting Bluetooth advertisement")
        self.connection_advertisement.register()
        # for security, a start should always result in a scheduled stop
        self.schedule_stop_advertisement()
        self.stopped = threading.Event()

    def schedule_stop_advertisement(self, timer_seconds=ADVERTISEMENT_SECONDS):
        if self.stop_advertisement_timer:
            logger.debug("cancelling existing stop advertisement timer")
            self.stop_advertisement_timer.cancel()

        # trigger the time to stop advertisement
        self.stop_advertisement_timer = threading.Timer(
            timer_seconds, self.stop_advertisement)
        self.stop_advertisement_timer.start()
        logger.debug('scheduled stop advertisement in %s seconds', timer_seconds)

    def stop_advertisement(self):
        logger.debug("Stopping Bluetooth advertisement")
        self.stopped.set()
        self.connection_advertisement.unregister()


    def run(self):
        logger.debug("Running BluetoothAdvertisementProcessor")
        self.start_advertisement()
        try:
            super().run()
        except Exception:
            logger.exception("BluetoothServicesProcessor #run failed for an unknown reason.")

if __name__ == "__main__":
    logger.debug("Starting BluetoothAdvertisementProcessor")
    ble_tools = BleTools()
    eth0_mac_address = "FF:FF:FF:FF:FF:FF"
    variant_details = {'APPNAME': 'Solaris'}
    bluetooth_advertisement_processor = BluetoothAdvertisementProcessor(
        eth0_mac_address, variant_details)
    
    threading.Thread(target=bluetooth_advertisement_processor.run).start()

    logger.debug("Finished BluetoothAdvertisementProcessor")



                