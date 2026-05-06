import pytest
from datetime import datetime
from src.analytics.domain import AnalyticsEvent


def test_analytics_event_valid():
    event = AnalyticsEvent(
        event_type="lead_created",
        occurred_at=datetime.utcnow(),
        entity_id="lead_123",
        payload={"source": "organic"}
    )
    assert event.event_type == "lead_created"


def test_analytics_event_invalid_payload():
    with pytest.raises(ValueError):
        AnalyticsEvent(
            event_type="x",
            occurred_at=datetime.utcnow(),
            entity_id="y",
            payload="not-a-dict"
        )
