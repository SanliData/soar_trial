from src.events.event_bus import InMemoryEventBus
from src.events.domain import DomainEvent
from datetime import datetime


def test_event_bus_emit_and_drain():
    bus = InMemoryEventBus()
    event = DomainEvent(
        event_name="test.event",
        occurred_at=datetime.utcnow(),
        payload={"a": 1},
    )

    bus.emit(event)
    drained = bus.drain()

    assert len(drained) == 1
    assert drained[0].event_name == "test.event"
