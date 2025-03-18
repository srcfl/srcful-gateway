import logging
import requests
from typing import List, Union, Tuple
import server.crypto.crypto as crypto
from server.app.blackboard import BlackBoard
from .itask import ITask


from .srcfulAPICallTask import SrcfulAPICallTask

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class InitializeTask(SrcfulAPICallTask):
    def __init__(
        self, event_time: int, bb: BlackBoard, wallet: str, dry_run: bool = False
    ):
        super().__init__(event_time, bb)
        self.is_initialized: bool | None = None
        self.post_url = "https://api.srcful.dev/"
        self.wallet = wallet
        self.dry_run = dry_run


    def get_id_and_wallet(self):
        with crypto.Chip() as chip:
            serial = chip.get_serial_number().hex()
            # pub_key = chip.get_public_key().hex()

            # id_and_wallet = serial + ":" + self.wallet + ":" + pub_key
            id_and_wallet = serial + ":" + self.wallet
            sign = chip.get_signature(id_and_wallet).hex()
        return id_and_wallet, sign, serial

    def _json(self):
        id_and_wallet, sign, serial = self.get_id_and_wallet()

        m = """
    mutation {
      gatewayInception {
        initialize(gatewayInitialization:{idAndWallet:"$var_idAndWallet", signature:"$var_sign"}) {
          initialized
        }
      }
    }
    """

        m = m.replace("$var_idAndWallet", id_and_wallet)
        m = m.replace("$var_sign", sign)

        if self.dry_run:
            m = m.replace(
                "gatewayInitialization:{idAndWallet",
                "gatewayInitialization:{dryRun:true, idAndWallet",
            )

        logger.info("Preparing intialization of wallet %s with sn %s", self.wallet, serial)
        logger.debug("Query: %s", m)

        return {"query": m}

    def _on_200(self, reply: requests.Response) -> Union[List[ITask], ITask, None]:
        if (
            reply.json()["data"]["gatewayInception"] is not None
            and reply.json()["data"]["gatewayInception"]["initialize"] is not None
            and reply.json()["data"]["gatewayInception"]["initialize"]["initialized"]
            is not None
        ):
            self.is_initialized = reply.json()["data"]["gatewayInception"]["initialize"]["initialized"]
        else:
            self.is_initialized = False
        return None

    def _on_error(self, reply: requests.Response) -> Union[int, Tuple[int, Union[List[ITask], ITask, None]]]:
        logger.warning("Failed to initialize wallet %s", self.wallet)
        return 0
