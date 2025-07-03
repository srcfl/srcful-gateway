import logging
import requests
from typing import List, Union
from .task import Task
from server.app.blackboard import BlackBoard

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class EvccHarvestTask(Task):
    """Task that harvests data from evcc API and sends it to configured harvest endpoints"""

    def __init__(self, event_time: int, bb: BlackBoard):
        super().__init__(event_time, bb)
        self.evcc_url = "http://localhost:7070/api/state"
        self.harvest_interval_ms = 10000  # 10 seconds

    def execute(self, event_time):
        try:
            # Fetch data from evcc API
            response = requests.get(self.evcc_url, timeout=5)

            if response.status_code == 200:
                evcc_data = response.json()

                # Prepare data for harvest endpoints
                harvest_data = {
                    "timestamp": self.bb.time_ms(),
                    "source": "evcc",
                    "data": evcc_data
                }

                logger.debug(f"Harvest data: {harvest_data}")

                # Send to all configured harvest endpoints
                for endpoint in self.bb.settings.harvest.endpoints:
                    try:
                        requests.post(endpoint, json=harvest_data, timeout=5)
                        logger.debug(f"Sent evcc data to {endpoint}")
                    except Exception as e:
                        logger.warning(f"Failed to send evcc data to {endpoint}: {e}")

                logger.debug(f"Harvested evcc data: {len(evcc_data)} fields")
            else:
                logger.warning(f"Failed to fetch evcc data: HTTP {response.status_code}")

        except Exception as e:
            logger.error(f"Error in evcc harvest task: {e}")

        # Schedule next execution
        self.time = event_time + self.harvest_interval_ms
        return [self]
