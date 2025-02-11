from datetime import datetime, timedelta
from enum import Enum
from typing import List
from server.backend.connection import Connection
from server.backend.histogram import Histogram, SolarHistogram


class DER:

    class Type(Enum):
        SOLAR = "Solar",
        ENERGY_METER = "EnergyMeter",
        BATTERY = "Battery",
        VEHICLE = "Vehicle"

    def __init__(self, serial:str, type:Type):
        self.serial = serial
        self.type = type

    def _construct_query(self, start_time:datetime, stop_time:datetime, resolution:Histogram.Resolution) -> str:
        return f"""
            query {{
                derData{{
                    {self.type.value}(sn:"{self.serial}") {{
                        {SolarHistogram.construct_query(self.serial, start_time, stop_time, resolution)}
                    }}
                }}
            }}
        """ 

    def histogram_from_now(self, connection: Connection, delta_time:timedelta, resolution:Histogram.Resolution) -> List[SolarHistogram.Data]:
        end_time = datetime.now()
        start_time = end_time - delta_time
        
        return self.histogram(connection, start_time, end_time, resolution)

    def histogram(self, connection: Connection, start_time:datetime, stop_time:datetime, resolution:Histogram.Resolution) -> List[SolarHistogram.Data]:
        query = self._construct_query(start_time, stop_time, resolution)

        response = connection.post(query)
        return SolarHistogram.from_dict(response["data"]["derData"][self.type.value][SolarHistogram._histogram_type_key])

