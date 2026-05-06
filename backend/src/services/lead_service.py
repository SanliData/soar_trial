"""
SERVICE: lead_service
PURPOSE: Lead management service for Google Ads Lead Form submissions
ENCODING: UTF-8 WITHOUT BOM
"""

import logging
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.models.lead import Lead
from src.models.appointment import Appointment
from src.models.user import User
from src.models.campaign import Campaign

logger = logging.getLogger(__name__)


class LeadService:
    """
    Service for managing leads from Google Ads Lead Forms.
    Handles lead creation, conversion to appointments, and status management.
    """
    
    def __init__(self, db: Session):
        """Initialize Lead Service with database session."""
        self.db = db
    
    def create_lead_from_google_ads(
        self,
        user_id: int,
        full_name: str,
        email: str,
        phone: Optional[str] = None,
        form_data: Optional[Dict[str, Any]] = None,
        google_ads_lead_id: Optional[str] = None,
        google_ads_campaign_id: Optional[str] = None,
        campaign_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a new lead from Google Ads Lead Form submission.
        
        Args:
            user_id: FinderOS user ID (campaign owner)
            full_name: Lead's full name
            email: Lead's email address
            phone: Lead's phone number (optional)
            form_data: Additional form data from Google Ads (JSON)
            google_ads_lead_id: Google Ads lead ID (unique identifier)
            google_ads_campaign_id: Google Ads campaign ID
            campaign_id: FinderOS campaign ID (optional)
        
        Returns:
            Dictionary with lead creation result
        """
        try:
            ***REMOVED*** Check if lead already exists (by Google Ads lead ID or email)
            existing_lead = None
            if google_ads_lead_id:
                existing_lead = self.db.query(Lead).filter(
                    Lead.google_ads_lead_id == google_ads_lead_id
                ).first()
            
            if not existing_lead and email:
                existing_lead = self.db.query(Lead).filter(
                    and_(
                        Lead.email == email,
                        Lead.user_id == user_id,
                        Lead.status.in_(["new", "contacted", "qualified"])
                    )
                ).first()
            
            if existing_lead:
                logger.info(f"Lead already exists: {existing_lead.id} (email: {email})")
                return {
                    "success": True,
                    "lead": existing_lead.to_dict(),
                    "is_duplicate": True,
                    "message": "Lead already exists"
                }
            
            ***REMOVED*** Create new lead
            lead = Lead(
                user_id=user_id,
                campaign_id=campaign_id,
                google_ads_campaign_id=google_ads_campaign_id,
                full_name=full_name,
                email=email,
                phone=phone,
                form_data=form_data or {},
                source="google_ads_lead_form",
                google_ads_lead_id=google_ads_lead_id,
                status="new"
            )
            
            self.db.add(lead)
            self.db.commit()
            self.db.refresh(lead)
            
            logger.info(f"Lead created: {lead.id} (email: {email}, user_id: {user_id})")
            
            ***REMOVED*** Send notification for new lead
            try:
                from src.services.notification_service import get_notification_service
                notification_service = get_notification_service(self.db)
                notification_service.notify_new_lead(
                    user_id=user_id,
                    lead_id=lead.id,
                    lead_name=full_name,
                    lead_email=email
                )
            except Exception as e:
                logger.warning(f"Failed to send lead notification: {str(e)}")
            
            ***REMOVED*** Automatically convert to appointment (Step 11)
            appointment_result = self.convert_lead_to_appointment(lead.id)
            
            return {
                "success": True,
                "lead": lead.to_dict(),
                "appointment": appointment_result.get("appointment"),
                "is_duplicate": False,
                "message": "Lead created and appointment scheduled"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating lead: {str(e)}")
            return {
                "success": False,
                "error": f"Error creating lead: {str(e)}"
            }
    
    def convert_lead_to_appointment(
        self,
        lead_id: int,
        scheduled_at: Optional[datetime] = None,
        duration_minutes: int = 30,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert a lead to an appointment (Step 11).
        Automatically called when a lead is created from Google Ads.
        
        Args:
            lead_id: Lead ID to convert
            scheduled_at: Appointment date/time (default: 24 hours from now)
            duration_minutes: Appointment duration in minutes
            title: Appointment title (default: "Follow-up: {Lead Name}")
            description: Appointment description
        
        Returns:
            Dictionary with appointment creation result
        """
        try:
            lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
            
            if not lead:
                return {
                    "success": False,
                    "error": "Lead not found"
                }
            
            if lead.appointment_id:
                ***REMOVED*** Appointment already exists
                appointment = self.db.query(Appointment).filter(
                    Appointment.id == lead.appointment_id
                ).first()
                return {
                    "success": True,
                    "appointment": appointment.to_dict() if appointment else None,
                    "message": "Appointment already exists"
                }
            
            ***REMOVED*** Set default scheduled time (24 hours from now)
            if not scheduled_at:
                scheduled_at = datetime.utcnow() + timedelta(hours=24)
            
            ***REMOVED*** Set default title
            if not title:
                title = f"Follow-up: {lead.full_name}"
            
            ***REMOVED*** Set default description
            if not description:
                description = f"Follow-up appointment for lead from Google Ads campaign. Email: {lead.email}"
                if lead.phone:
                    description += f", Phone: {lead.phone}"
            
            ***REMOVED*** Get user email for calendar integration
            user = self.db.query(User).filter(User.id == lead.user_id).first()
            user_email = user.email if user else None
            
            ***REMOVED*** Create appointment
            appointment = Appointment(
                user_id=lead.user_id,
                campaign_id=lead.campaign_id,
                title=title,
                description=description,
                scheduled_at=scheduled_at,
                duration_minutes=duration_minutes,
                location="Virtual",  ***REMOVED*** Default to virtual meeting
                contact_name=lead.full_name,
                contact_email=lead.email,
                contact_phone=lead.phone,
                status="scheduled",
                notes=f"Auto-created from Google Ads Lead Form. Lead ID: {lead.id}"
            )
            
            self.db.add(appointment)
            self.db.commit()
            self.db.refresh(appointment)
            
            ***REMOVED*** Create Google Calendar event if user email is available
            meet_link = None
            calendar_event_id = None
            if user_email:
                try:
                    from src.services.calendar_service import get_calendar_service
                    calendar_service = get_calendar_service()
                    
                    calendar_result = calendar_service.create_appointment_event(
                        user_email=user_email,
                        lead_email=lead.email,
                        lead_name=lead.full_name,
                        start_time=scheduled_at,
                        duration_minutes=duration_minutes,
                        title=title,
                        description=description,
                        create_google_meet=True
                    )
                    
                    if calendar_result.get("success"):
                        meet_link = calendar_result.get("meet_link")
                        calendar_event_id = calendar_result.get("event_id")
                        
                        ***REMOVED*** Update appointment with Google Meet link
                        appointment.meeting_url = meet_link
                        self.db.commit()
                        
                        logger.info(f"Google Calendar event created: {calendar_event_id}")
                except Exception as e:
                    logger.warning(f"Failed to create Google Calendar event: {str(e)}")
                    ***REMOVED*** Continue without calendar event
            
            ***REMOVED*** Update lead with appointment reference
            lead.appointment_id = appointment.id
            lead.status = "appointment_scheduled"
            lead.converted_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Lead {lead_id} converted to appointment {appointment.id}")
            
            ***REMOVED*** Refresh appointment to get updated meeting_url
            self.db.refresh(appointment)
            
            ***REMOVED*** Send notification for new appointment
            try:
                from src.services.notification_service import get_notification_service
                notification_service = get_notification_service(self.db)
                notification_service.notify_new_appointment(
                    user_id=lead.user_id,
                    appointment_id=appointment.id,
                    lead_name=lead.full_name,
                    scheduled_at=scheduled_at,
                    meet_link=meet_link
                )
            except Exception as e:
                logger.warning(f"Failed to send appointment notification: {str(e)}")
            
            return {
                "success": True,
                "appointment": appointment.to_dict(),
                "calendar_event_id": calendar_event_id,
                "meet_link": meet_link,
                "message": "Appointment created successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error converting lead to appointment: {str(e)}")
            return {
                "success": False,
                "error": f"Error converting lead to appointment: {str(e)}"
            }
    
    def get_leads_by_user(
        self,
        user_id: int,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get leads for a specific user.
        
        Args:
            user_id: FinderOS user ID
            status: Optional status filter
            limit: Maximum number of leads to return
        
        Returns:
            List of lead dictionaries
        """
        try:
            query = self.db.query(Lead).filter(Lead.user_id == user_id)
            
            if status:
                query = query.filter(Lead.status == status)
            
            leads = query.order_by(Lead.created_at.desc()).limit(limit).all()
            
            return [lead.to_dict() for lead in leads]
            
        except Exception as e:
            logger.error(f"Error getting leads: {str(e)}")
            return []
    
    def update_lead_status(
        self,
        lead_id: int,
        status: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update lead status.
        
        Args:
            lead_id: Lead ID
            status: New status
            notes: Optional notes
        
        Returns:
            Dictionary with update result
        """
        try:
            lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
            
            if not lead:
                return {
                    "success": False,
                    "error": "Lead not found"
                }
            
            lead.status = status
            if notes:
                lead.notes = notes
            
            self.db.commit()
            self.db.refresh(lead)
            
            return {
                "success": True,
                "lead": lead.to_dict(),
                "message": "Lead status updated"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating lead status: {str(e)}")
            return {
                "success": False,
                "error": f"Error updating lead status: {str(e)}"
            }


def get_lead_service(db: Session) -> LeadService:
    """
    Get LeadService instance with database session.
    """
    return LeadService(db)

