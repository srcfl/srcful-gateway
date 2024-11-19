from datetime import datetime
from enum import Enum
from typing import Dict, List


class Histogram:
    class Resolution():
        class Type(Enum):
            SECOND = "s"
            MINUTE = "m"
            HOUR = "h"
            DAY = "d"

        def __init__(self, type:Type, count:int = 1):
            self.type = type
            self.count = count

        @property
        def value(self) -> str:
            return f"{self.count}{self.type.value}"
        
    

class SolarHistogram:

    _ts_key:str = "ts"
    _power_key:str = "power"
    _histogram_type_key:str = "histogram"

    @classmethod
    def construct_query(cls, serial:str, start_time:datetime, end_time:datetime, resolution:Histogram.Resolution) -> str:
        query = f"""
                {cls._histogram_type_key}(start: "{start_time.isoformat()}", stop: "{end_time.isoformat()}", resolution: "{resolution.value}") {{
                    {cls._ts_key}
                    {cls._power_key}
                }}
        """
        return query

    @classmethod
    def from_dict(cls, data:Dict) -> List["SolarHistogram.Data"]:
        return [cls.Data(datetime.fromisoformat(item[cls._ts_key]), item[cls._power_key]) for item in data]

    class Data:
        def __init__(self, ts:datetime, power:float):
            self._ts = ts
            self._power = power

        @property
        def ts(self) -> datetime:
            return self._ts

        @property
        def power(self) -> float:
            return self._power
