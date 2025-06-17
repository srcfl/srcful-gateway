import json
import sqlite3
import logging
from typing import Dict, Any, List, Optional

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

    def add_connection(self, connection: Dict[str, Any]) -> bool:
        if not isinstance(connection, dict) or 'sn' not in connection or not connection.get('sn'):
            logger.error(f"Invalid connection data: {connection}")
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
                sn = connection.get('sn')
                updated = False
                for i, c in enumerate(connections):
                    if isinstance(c, dict) and c.get('sn') == sn:
                        connections[i] = connection
                        updated = True
                        logger.info(f"Updated existing connection for SN: {sn}")
                        break

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
                for connection in connections:
                    if isinstance(connection, dict) and connection.get('sn') == sn:
                        connection_to_remove = connection
                        break

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
