from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any


@dataclass(frozen=True)
class DomainEvent:
    event_name: str
    occurred_at: datetime
    payload: Dict[str, Any]

    def __post_init__(self):
        if not self.event_name:
            raise ValueError("event_name cannot be empty")
        if not isinstance(self.payload, dict):
            raise ValueError("payload must be a dict")
