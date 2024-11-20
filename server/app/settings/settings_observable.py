from __future__ import annotations
from enum import Enum
from typing import Callable, List, Optional


class ChangeSource(Enum):
    LOCAL = 1
    BACKEND = 2

class Observable:
    def __init__(self, parent: Optional[Observable] = None):
        self._listeners: List[Callable[[ChangeSource], None]] = []
        self._parent = parent

    def add_listener(self, listener: Callable[[ChangeSource], None]):
        if listener not in self._listeners:
            self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[ChangeSource], None]):
        if listener in self._listeners:
            self._listeners.remove(listener)

    def notify_listeners(self, source: ChangeSource):
        for listener in self._listeners:
            listener(source)
        if self._parent:
            self._parent.notify_listeners(source)