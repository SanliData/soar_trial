from typing import List
from src.events.domain import DomainEvent


class InMemoryEventBus:
    def __init__(self):
        self._events: List[DomainEvent] = []

    def emit(self, event: DomainEvent) -> None:
        self._events.append(event)

    def drain(self) -> List[DomainEvent]:
        events = list(self._events)
        self._events.clear()
        return events
