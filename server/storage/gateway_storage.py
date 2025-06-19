import json
import sqlite3
import logging
from typing import Dict, Any, List, Optional
from server.devices.ICom import ICom
from server.devices.IComFactory import IComFactory

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class GatewayStorage:
    def __init__(self, db_path: str = "/data/srcful/gateway.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            # Enable WAL mode for better concurrent access
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS storage (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            ''')

    def add_connection(self, device: ICom) -> bool:
        """Add a device connection to storage.

        Args:
            device: ICom object

        Returns:
            True if connection was added/updated successfully, False otherwise
        """
        if not isinstance(device, ICom):
            logger.error(f"Invalid device type: {type(device)}. Expected ICom object.")
            return False

        connection = device.get_config()
        sn = device.get_SN()

        if not sn:
            logger.error(f"Invalid device - no serial number found: {connection}")
            return False

        try:
            with sqlite3.connect(self.db_path) as conn:
                # Ensure connections key exists
                conn.execute("INSERT OR IGNORE INTO storage (key, value) VALUES ('connections', '[]')")

                # Get current connections
                result = conn.execute("SELECT value FROM storage WHERE key = 'connections'").fetchone()
                connections = json.loads(result[0]) if result else []

                # Ensure it's a list
                if not isinstance(connections, list):
                    connections = []

                # Check if SN already exists and update it
                updated = False
                for i, stored_config in enumerate(connections):
                    if isinstance(stored_config, dict):
                        try:
                            stored_device = IComFactory.create_com(stored_config)
                            if stored_device.get_SN() == sn:
                                connections[i] = connection
                                updated = True
                                logger.info(f"Updated existing connection for SN: {sn}. Was: {stored_config}, and now: {connection}")
                                break
                        except Exception as e:
                            logger.warning(f"Could not create device from stored config: {e}")
                            continue

                # If not found, add as new connection
                if not updated:
                    connections.append(connection)
                    logger.info(f"Added new connection for SN: {sn}")

                conn.execute("UPDATE storage SET value = ? WHERE key = 'connections'", (json.dumps(connections),))
                return True
        except Exception as e:
            logger.error(f"Failed to add connection: {e}")
            return False

    def remove_connection(self, sn: str) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                result = conn.execute("SELECT value FROM storage WHERE key = 'connections'").fetchone()
                if not result:
                    return False

                connections = json.loads(result[0])
                if not isinstance(connections, list):
                    return False

                # Find the connection to remove
                connection_to_remove = None
                for stored_config in connections:
                    if isinstance(stored_config, dict):
                        try:
                            stored_device = IComFactory.create_com(stored_config)
                            if stored_device.get_SN() == sn:
                                connection_to_remove = stored_config
                                break
                        except Exception as e:
                            logger.warning(f"Could not create device from stored config: {e}")
                            continue

                if connection_to_remove is None:
                    return False

                # Remove the specific connection
                connections.remove(connection_to_remove)
                conn.execute("UPDATE storage SET value = ? WHERE key = 'connections'", (json.dumps(connections),))
                logger.info(f"Removed connection for SN: {sn}")
                return True
        except Exception as e:
            logger.error(f"Failed to remove connection: {e}")
            return False

    def get_connections(self) -> List[Dict[str, Any]]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                result = conn.execute("SELECT value FROM storage WHERE key = 'connections'").fetchone()
                if not result:
                    return []

                connections = json.loads(result[0])
                if not isinstance(connections, list):
                    return []

                # Return only valid dicts
                return [c for c in connections if isinstance(c, dict)]
        except Exception as e:
            logger.error(f"Failed to get connections: {e}")
            return []

    def connection_exists(self, device: ICom) -> bool:
        connections = self.get_connections()
        for connection in connections:
            d = IComFactory.create_com(connection)
            if d.get_SN() == device.get_SN():
                return True
        return False

    def save_settings(self, settings: Dict[str, Any]) -> bool:
        if not isinstance(settings, dict):
            return False
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("INSERT OR REPLACE INTO storage (key, value) VALUES ('settings', ?)", (json.dumps(settings),))
            return True
        except Exception:
            return False

    def get_settings(self) -> Optional[Dict[str, Any]]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                result = conn.execute("SELECT value FROM storage WHERE key = 'settings'").fetchone()
                if not result:
                    return None
                settings = json.loads(result[0])
                return settings if isinstance(settings, dict) else None
        except Exception:
            return None
