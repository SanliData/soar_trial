import pytest
from datetime import datetime
from src.records.domain import Record, RecordStatusChange


def test_record_valid():
    record = Record(
        record_id="r1",
        owner_id="u1",
        created_at=datetime.utcnow(),
        status="pending",
        data={"key": "value"}
    )
    assert record.status == "pending"


def test_record_invalid_status():
    with pytest.raises(ValueError):
        Record(
            record_id="r1",
            owner_id="u1",
            created_at=datetime.utcnow(),
            status="invalid",
            data={}
        )


def test_record_status_change_valid():
    change = RecordStatusChange(
        record_id="r1",
        old_status="pending",
        new_status="active",
        changed_at=datetime.utcnow()
    )
    assert change.old_status != change.new_status


def test_record_status_change_invalid():
    with pytest.raises(ValueError):
        RecordStatusChange(
            record_id="r1",
            old_status="active",
            new_status="active",
            changed_at=datetime.utcnow()
        )
