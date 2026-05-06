from datetime import datetime
from src.events.domain import DomainEvent


def analytics_event(event_type: str, payload: dict) -> DomainEvent:
    return DomainEvent(
        event_name=f"analytics.{event_type}",
        occurred_at=datetime.utcnow(),
        payload=payload,
    )
