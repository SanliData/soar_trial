from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Dict, Any

from src.records.domain import Record

router = APIRouter(prefix="/records", tags=["records"])


@router.post("/preview")
def preview_record(payload: Dict[str, Any]):
    try:
        record = Record(
            record_id=payload.get("record_id"),
            owner_id=payload.get("owner_id"),
            created_at=datetime.utcnow(),
            status=payload.get("status", "pending"),
            data=payload.get("data", {}),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "status": "ok",
        "record_id": record.record_id,
        "owner_id": record.owner_id,
        "record_status": record.status,
    }
