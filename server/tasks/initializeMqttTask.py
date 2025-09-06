#!/usr/bin/env python3
"""
Initialize MQTT Service Task

A task that initializes the MQTT service by fetching the owner wallet
and creating the MQTT service instance.
"""

import logging
import requests
from server.tasks.task import Task
from server.backend.mqtt_service import MQTTService

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)


class InitializeMqttTask(Task):
    def __init__(self, time, bb, web_host: tuple[str, int]):
        super().__init__(time, bb)
        self.web_host = web_host

    def get_owner_wallet(self) -> str:
        """Fetch owner wallet address from local web server"""
        try:
            # Use localhost instead of 0.0.0.0 for internal HTTP requests
            host = "127.0.0.1" if self.web_host[0] == "0.0.0.0" else self.web_host[0]
            url = f"http://{host}:{self.web_host[1]}/api/owner"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            owner_info = response.json()
            wallet = owner_info.get('wallet')
            
            if not wallet:
                raise ValueError("No wallet found in owner info")
            
            logger.info(f"Retrieved wallet address: {wallet}")
            return wallet
            
        except Exception as e:
            logger.error(f"Failed to get owner wallet from {url}: {e}")
            raise

    def execute(self, time_now):
        """Execute the MQTT initialization task"""
        try:
            # Only initialize if MQTT service is not already set
            if self.bb.mqtt_service:
                logger.info("MQTT service already initialized, skipping")
                return
                
            logger.info("Initializing MQTT service...")
            wallet_address = self.get_owner_wallet()
            mqtt_service = MQTTService.create_and_start(self.bb, wallet_address)
            self.bb.set_mqtt_service(mqtt_service)
            logger.info("MQTT service successfully initialized and started")
            
        except Exception as e:
            logger.error(f"Failed to initialize MQTT service: {e}")
            # Reschedule the task to retry in 30 seconds
            logger.info("Rescheduling MQTT initialization in 30 seconds")
            self.bb.add_task(InitializeMqttTask(time_now + 30000, self.bb, self.web_host))

    def __str__(self):
        return f"InitializeMqttTask(time={self.time})"
