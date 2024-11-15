"""
Interface for system time
"""

from abc import ABC, abstractmethod

class ISystemTime(ABC):
    @abstractmethod
    def time_ms(self) -> int:
        pass

    @abstractmethod
    def elapsed_time(self) -> int:
        pass
