from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional


@dataclass(frozen=True)
class Record:
    record_id: str
    owner_id: str
    created_at: datetime
    status: str
    data: Dict[str, Any]

    def __post_init__(self):
        if not self.record_id:
            raise ValueError("record_id cannot be empty")
        if not self.owner_id:
            raise ValueError("owner_id cannot be empty")
        if self.status not in {"pending", "active", "archived"}:
            raise ValueError("invalid record status")
        if not isinstance(self.data, dict):
            raise ValueError("data must be a dictionary")


@dataclass(frozen=True)
class RecordStatusChange:
    record_id: str
    old_status: str
    new_status: str
    changed_at: datetime

    def __post_init__(self):
        if self.old_status == self.new_status:
            raise ValueError("status must actually change")
