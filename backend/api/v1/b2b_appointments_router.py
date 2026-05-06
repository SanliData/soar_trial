***REMOVED*** -*- coding: utf-8 -*-
"""
B2B Appointments Router - Randevu yönetimi API endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from backend.services.b2b import appointment_service
from backend.models.b2b_appointment import Appointment

router = APIRouter(prefix="/api/v1/b2b/appointments", tags=["B2B"])


class AppointmentCreate(BaseModel):
    campaign_id: int
    persona_id: int
    title: str
    scheduled_at: datetime
    description: Optional[str] = None
    duration_minutes: int = 30
    contact_method: str = "email"
    location_type: str = "virtual"
    meeting_link: Optional[str] = None
    location_address: Optional[str] = None


@router.post("/", response_model=dict)
async def create_appointment(appointment_data: AppointmentCreate):
    """Yeni randevu oluştur"""
    try:
        appointment = appointment_service.create_appointment(
            campaign_id=appointment_data.campaign_id,
            persona_id=appointment_data.persona_id,
            title=appointment_data.title,
            scheduled_at=appointment_data.scheduled_at,
            description=appointment_data.description,
            duration_minutes=appointment_data.duration_minutes,
            contact_method=appointment_data.contact_method,
            location_type=appointment_data.location_type,
            meeting_link=appointment_data.meeting_link,
            location_address=appointment_data.location_address
        )
        return appointment.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{appointment_id}", response_model=dict)
async def get_appointment(appointment_id: int):
    """Randevu detayı"""
    appointment = appointment_service.get_appointment_by_id(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment.to_dict()


@router.post("/{appointment_id}/confirm", response_model=dict)
async def confirm_appointment(appointment_id: int):
    """Randevuyu onayla"""
    appointment = appointment_service.confirm_appointment(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment.to_dict()


@router.post("/{appointment_id}/reschedule", response_model=dict)
async def reschedule_appointment(
    appointment_id: int,
    new_scheduled_at: datetime
):
    """Randevuyu yeniden planla"""
    appointment = appointment_service.reschedule_appointment(
        appointment_id,
        new_scheduled_at
    )
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment.to_dict()


@router.post("/{appointment_id}/complete", response_model=dict)
async def complete_appointment(
    appointment_id: int,
    outcome: str,
    outcome_notes: Optional[str] = None,
    next_steps: Optional[str] = None
):
    """Randevuyu tamamla"""
    appointment = appointment_service.complete_appointment(
        appointment_id,
        outcome=outcome,
        outcome_notes=outcome_notes,
        next_steps=next_steps
    )
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment.to_dict()


@router.post("/{appointment_id}/cancel", response_model=dict)
async def cancel_appointment(
    appointment_id: int,
    reason: Optional[str] = None
):
    """Randevuyu iptal et"""
    appointment = appointment_service.cancel_appointment(
        appointment_id,
        reason=reason
    )
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment.to_dict()


@router.get("/", response_model=dict)
async def get_appointments(
    campaign_id: Optional[int] = Query(None),
    persona_id: Optional[int] = Query(None),
    upcoming_days: Optional[int] = Query(None, ge=1, le=365)
):
    """Randevu listesi"""
    try:
        if campaign_id:
            appointments = appointment_service.get_appointments_by_campaign(campaign_id)
        elif persona_id:
            appointments = appointment_service.get_appointments_by_persona(persona_id)
        elif upcoming_days:
            appointments = appointment_service.get_upcoming_appointments(days_ahead=upcoming_days)
        else:
            appointments = []
        
        return {
            "total": len(appointments),
            "appointments": [a.to_dict() for a in appointments]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/statistics/overview", response_model=dict)
async def get_appointment_statistics(
    campaign_id: Optional[int] = Query(None)
):
    """Randevu istatistikleri"""
    return appointment_service.get_appointment_statistics(campaign_id=campaign_id)

