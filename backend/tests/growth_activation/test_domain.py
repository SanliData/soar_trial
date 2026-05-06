"""
TESTS: Growth & Activation domain
SCOPE: ROL-3 deterministic validation
"""

from datetime import datetime

from src.growth_activation.supply_sources import SupplySource
from src.growth_activation.geo_targeting_rules import GeoTargetRule
from src.growth_activation.activation_events import ActivationEvent


def test_supply_source_creation():
    s = SupplySource(
        source_type="organic_signup",
        description="test"
    )
    assert s.source_type == "organic_signup"
    assert s.description == "test"


def test_geo_target_rule_contains():
    rule = GeoTargetRule(
        center_lat=0.0,
        center_lng=0.0,
        radius_meters=100
    )
    assert rule.contains(0.0, 0.0) is True


def test_activation_event_creation():
    e = ActivationEvent(
        event_type="activated",
        occurred_at=datetime.utcnow(),
        entity_id="x",
        metadata={}
    )
    assert e.event_type == "activated"
    assert e.entity_id == "x"
