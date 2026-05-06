from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any


@dataclass(frozen=True)
class AnalyticsEvent:
    event_type: str
    occurred_at: datetime
    entity_id: str
    payload: Dict[str, Any]

    def __post_init__(self):
        if not self.event_type:
            raise ValueError("event_type cannot be empty")
        if not isinstance(self.payload, dict):
            raise ValueError("payload must be a dictionary")
