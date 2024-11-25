import json
from typing import Dict, List

import requests

from server.backend.connection import Connection
from server.backend.der import DER


class Gateway:

    _sn_key:str = "sn"
    _type_key:str = "type"

    def __init__(self, serial:str):
        self.serial = serial

    @classmethod
    def str_2_type(cls, str_type:str) -> DER.Type:
        match str_type:
            case "solar" | "Solar":
                return DER.Type.SOLAR
            case _:
                raise ValueError(f"Invalid DER type: {str_type}")
            
    @classmethod
    def dict_2_ders(cls, data:Dict) -> List[DER]:
        return [DER(item[cls._sn_key], Gateway.str_2_type(item[cls._type_key])) for item in data]
    
    @classmethod
    def _get_ders_query(cls, serial: str) -> str:
        return f"""
            query {{
                gateway {{
                    gateway(id:"{serial}") {{
                        ders {{
                            {cls._sn_key}
                            {cls._type_key} 
                        }}
                    }}
                }}
            }} 
        """

    def get_ders(self, connection: Connection) -> List[DER]:
        query = Gateway._get_ders_query(self.serial)

        response = connection.post(query)

        return Gateway.dict_2_ders(response["data"]["gateway"]["gateway"]["ders"])
    
    @classmethod
    def _get_globals_query(cls, serial: str, timestamp: str, signed_id_and_timestamp: str, key: str) -> str:
        return f"""
            query {{
                    globalConfiguration{{
                        configuration(deviceAuth:{{
                            id:"{serial}",
                            timestamp:"{timestamp}",
                            signedIdAndTimestamp:"{signed_id_and_timestamp}",
                            key:"{key}"
                        }})
                    }}
                }}
        """

    def get_globals(self, connection: Connection, timestamp: str, signed_id_and_timestamp: str, key: str) -> Dict:
        query = Gateway._get_globals_query(self.serial, timestamp, signed_id_and_timestamp, key)
        response = connection.post(query)
        return json.loads(response["data"]["globalConfiguration"]["configuration"])
