from datetime import datetime
from src.events.domain import DomainEvent


def record_event(event_type: str, payload: dict) -> DomainEvent:
    return DomainEvent(
        event_name=f"records.{event_type}",
        occurred_at=datetime.utcnow(),
        payload=payload,
    )
