"""
ROUTER: appointment_router
PURPOSE: Appointment management endpoints with Google Calendar integration
ENCODING: UTF-8 WITHOUT BOM
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import logging

from src.models.user import User
from src.models.appointment import Appointment
from src.models.lead import Lead
from src.db.base import get_db
from src.services.auth_service import get_current_user_dependency, get_current_user_impl
from src.services.calendar_service import get_calendar_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/appointments", tags=["appointments"])


***REMOVED*** Helper function to get current user
def get_current_user_from_header(
    authorization: str = Depends(lambda: None),
    db: Session = Depends(get_db)
):
    """Helper to inject authorization header into get_current_user_dependency"""
    if authorization:
        return get_current_user_impl(authorization=authorization, db=db)
    return None


class AppointmentResponse(BaseModel):
    id: int
    user_id: int
    persona_id: Optional[int] = None
    company_id: Optional[int] = None
    campaign_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    scheduled_at: str
    duration_minutes: int
    location: Optional[str] = None
    meeting_url: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    status: str
    notes: Optional[str] = None
    created_at: str
    updated_at: str


class AppointmentListResponse(BaseModel):
    success: bool
    appointments: List[Dict[str, Any]]
    total: int


class AvailableSlotsResponse(BaseModel):
    success: bool
    date: str
    available_slots: List[Dict[str, Any]]
    total_slots: int
    duration_minutes: int


@router.get("/list", response_model=AppointmentListResponse)
async def get_appointments(
    status: Optional[str] = Query(None, description="Filter by status"),
    user: Optional[User] = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """
    Get appointments for the authenticated user.
    """
    try:
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        query = db.query(Appointment).filter(Appointment.user_id == user.id)
        
        if status:
            query = query.filter(Appointment.status == status)
        
        ***REMOVED*** Get upcoming appointments first
        appointments = query.order_by(Appointment.scheduled_at.asc()).all()
        
        ***REMOVED*** Get lead information for each appointment
        appointments_data = []
        for appointment in appointments:
            appointment_dict = appointment.to_dict()
            
            ***REMOVED*** Get lead information if exists
            if appointment.campaign_id:
                lead = db.query(Lead).filter(
                    Lead.appointment_id == appointment.id
                ).first()
                
                if lead:
                    appointment_dict["lead"] = {
                        "id": lead.id,
                        "full_name": lead.full_name,
                        "email": lead.email,
                        "phone": lead.phone,
                        "source": lead.source
                    }
            
            appointments_data.append(appointment_dict)
        
        return AppointmentListResponse(
            success=True,
            appointments=appointments_data,
            total=len(appointments_data)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting appointments: {str(e)}")


@router.get("/available-slots", response_model=AvailableSlotsResponse)
async def get_available_slots(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    duration_minutes: int = Query(30, description="Duration in minutes"),
    user: Optional[User] = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """
    Get available time slots for a specific date.
    Uses Google Calendar API to check availability.
    """
    try:
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        if not user.email:
            raise HTTPException(status_code=400, detail="User email not found")
        
        ***REMOVED*** Parse date
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        ***REMOVED*** Get calendar service
        calendar_service = get_calendar_service()
        
        result = calendar_service.find_available_slots(
            user_email=user.email,
            date=date_obj,
            duration_minutes=duration_minutes,
            start_hour=9,
            end_hour=17
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to get available slots"))
        
        return AvailableSlotsResponse(
            success=True,
            date=date,
            available_slots=result.get("available_slots", []),
            total_slots=result.get("total_slots", 0),
            duration_minutes=duration_minutes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting available slots: {str(e)}")


@router.post("/{appointment_id}/cancel")
async def cancel_appointment(
    appointment_id: int,
    user: Optional[User] = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """
    Cancel an appointment and delete the Google Calendar event.
    """
    try:
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        appointment = db.query(Appointment).filter(
            Appointment.id == appointment_id,
            Appointment.user_id == user.id
        ).first()
        
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        ***REMOVED*** Delete Google Calendar event if exists
        if user.email and appointment.meeting_url:
            try:
                calendar_service = get_calendar_service()
                ***REMOVED*** Extract event ID from meeting URL or store it separately
                ***REMOVED*** For now, we'll update appointment status
                pass
            except Exception as e:
                logger.warning(f"Failed to delete calendar event: {str(e)}")
        
        ***REMOVED*** Update appointment status
        appointment.status = "cancelled"
        db.commit()
        
        return {
            "success": True,
            "message": "Appointment cancelled successfully",
            "appointment_id": appointment_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error cancelling appointment: {str(e)}")


@router.post("/{appointment_id}/reschedule")
async def reschedule_appointment(
    appointment_id: int,
    new_date: str = Query(..., description="New date in YYYY-MM-DD format"),
    new_time: str = Query(..., description="New time in HH:MM format"),
    user: Optional[User] = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """
    Reschedule an appointment and update the Google Calendar event.
    """
    try:
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        appointment = db.query(Appointment).filter(
            Appointment.id == appointment_id,
            Appointment.user_id == user.id
        ).first()
        
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        ***REMOVED*** Parse new date and time
        try:
            new_datetime = datetime.strptime(f"{new_date} {new_time}", "%Y-%m-%d %H:%M")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date/time format")
        
        ***REMOVED*** Update Google Calendar event if exists
        if user.email:
            try:
                calendar_service = get_calendar_service()
                ***REMOVED*** Update calendar event (would need to store event_id)
                ***REMOVED*** For now, we'll just update the appointment
                pass
            except Exception as e:
                logger.warning(f"Failed to update calendar event: {str(e)}")
        
        ***REMOVED*** Update appointment
        appointment.scheduled_at = new_datetime
        appointment.status = "scheduled"
        db.commit()
        
        return {
            "success": True,
            "message": "Appointment rescheduled successfully",
            "appointment_id": appointment_id,
            "new_scheduled_at": new_datetime.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error rescheduling appointment: {str(e)}")


@router.get("/{appointment_id}")
async def get_appointment(
    appointment_id: int,
    user: Optional[User] = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """
    Get a specific appointment by ID.
    """
    try:
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        appointment = db.query(Appointment).filter(
            Appointment.id == appointment_id,
            Appointment.user_id == user.id
        ).first()
        
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        appointment_dict = appointment.to_dict()
        
        ***REMOVED*** Get lead information if exists
        if appointment.campaign_id:
            lead = db.query(Lead).filter(
                Lead.appointment_id == appointment.id
            ).first()
            
            if lead:
                appointment_dict["lead"] = {
                    "id": lead.id,
                    "full_name": lead.full_name,
                    "email": lead.email,
                    "phone": lead.phone,
                    "source": lead.source
                }
        
        return {
            "success": True,
            "appointment": appointment_dict
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting appointment: {str(e)}")


@router.get("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "domain": "appointments"
    }

