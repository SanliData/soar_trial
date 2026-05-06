***REMOVED*** -*- coding: utf-8 -*-
"""
Appointment Service - Appointment creation and management service
Reaches out to target individuals and creates appointments
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.models.b2b_appointment import Appointment, AppointmentStatus
from backend.models.b2b_campaign import Campaign
from backend.models.b2b_persona import Persona
from backend.db import SessionLocal
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

from backend.src.config.settings import get_int_env


class AppointmentService:
    """Appointment creation and management service"""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER") or "smtp.gmail.com"
        self.smtp_port = get_int_env("SMTP_PORT", 587)
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
    
    def _get_db(self) -> Session:
        """Get database session"""
        return SessionLocal()
    
    def create_appointment(
        self,
        campaign_id: int,
        persona_id: int,
        title: str,
        scheduled_at: datetime,
        description: Optional[str] = None,
        duration_minutes: int = 30,
        contact_method: str = "email",
        location_type: str = "virtual",
        meeting_link: Optional[str] = None,
        location_address: Optional[str] = None
    ) -> Appointment:
        """Create new appointment"""
        db = self._get_db()
        try:
            ***REMOVED*** Check campaign and persona
            campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
            persona = db.query(Persona).filter(Persona.id == persona_id).first()
            
            if not campaign or not persona:
                raise ValueError("Campaign or Persona not found")
            
            appointment = Appointment(
                campaign_id=campaign_id,
                persona_id=persona_id,
                title=title,
                description=description,
                status=AppointmentStatus.PENDING.value,
                scheduled_at=scheduled_at,
                duration_minutes=duration_minutes,
                timezone="UTC",
                contact_method=contact_method,
                location_type=location_type,
                meeting_link=meeting_link,
                location_address=location_address,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(appointment)
            db.commit()
            db.refresh(appointment)
            
            ***REMOVED*** Send notification when appointment is created
            self._send_appointment_notification(appointment, persona)
            
            return appointment
        finally:
            db.close()
    
    def _send_appointment_notification(self, appointment: Appointment, persona: Persona):
        """Send appointment notification (email, LinkedIn, etc.)"""
        if appointment.contact_method == "email" and persona.email:
            self._send_email_notification(appointment, persona)
        elif appointment.contact_method == "linkedin" and persona.linkedin_url:
            ***REMOVED*** Send LinkedIn message (requires LinkedIn API)
            pass
    
    def _send_email_notification(self, appointment: Appointment, persona: Persona):
        """Send appointment notification via email"""
        if not self.smtp_username or not self.smtp_password:
            print("SMTP credentials not configured. Skipping email notification.")
            return
        
        if not persona.email:
            return
        
        try:
            msg = MIMEMultipart()
            msg["From"] = self.smtp_username
            msg["To"] = persona.email
            msg["Subject"] = f"Appointment Request: {appointment.title}"
            
            body = f"""
            Dear {persona.full_name},
            
            We have an appointment request regarding {appointment.title}.
            
            Date: {appointment.scheduled_at.strftime('%Y-%m-%d %H:%M')}
            Duration: {appointment.duration_minutes} minutes
            
            {appointment.description or ''}
            
            """
            
            if appointment.location_type == "virtual" and appointment.meeting_link:
                body += f"\nMeeting Link: {appointment.meeting_link}\n"
            elif appointment.location_type == "in_person" and appointment.location_address:
                body += f"\nAddress: {appointment.location_address}\n"
            
            msg.attach(MIMEText(body, "plain", "utf-8"))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            ***REMOVED*** Mark notification as sent
            db = self._get_db()
            try:
                appointment.reminder_sent = True
                appointment.reminder_sent_at = datetime.utcnow()
                db.commit()
            finally:
                db.close()
            
        except Exception as e:
            print(f"Email notification error: {e}")
    
    def confirm_appointment(self, appointment_id: int) -> Optional[Appointment]:
        """Confirm appointment"""
        db = self._get_db()
        try:
            appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
            
            if not appointment:
                return None
            
            appointment.status = AppointmentStatus.CONFIRMED.value
            appointment.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(appointment)
            
            return appointment
        finally:
            db.close()
    
    def reschedule_appointment(
        self,
        appointment_id: int,
        new_scheduled_at: datetime
    ) -> Optional[Appointment]:
        """Reschedule appointment"""
        db = self._get_db()
        try:
            appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
            
            if not appointment:
                return None
            
            appointment.scheduled_at = new_scheduled_at
            appointment.status = AppointmentStatus.RESCHEDULED.value
            appointment.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(appointment)
            
            ***REMOVED*** Send notification for new date
            persona = db.query(Persona).filter(Persona.id == appointment.persona_id).first()
            if persona:
                self._send_appointment_notification(appointment, persona)
            
            return appointment
        finally:
            db.close()
    
    def complete_appointment(
        self,
        appointment_id: int,
        outcome: str,
        outcome_notes: Optional[str] = None,
        next_steps: Optional[str] = None
    ) -> Optional[Appointment]:
        """Complete appointment and save result"""
        db = self._get_db()
        try:
            appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
            
            if not appointment:
                return None
            
            appointment.status = AppointmentStatus.COMPLETED.value
            appointment.outcome = outcome
            appointment.outcome_notes = outcome_notes
            appointment.next_steps = next_steps
            appointment.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(appointment)
            
            return appointment
        finally:
            db.close()
    
    def cancel_appointment(self, appointment_id: int, reason: Optional[str] = None) -> Optional[Appointment]:
        """Cancel appointment"""
        db = self._get_db()
        try:
            appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
            
            if not appointment:
                return None
            
            appointment.status = AppointmentStatus.CANCELLED.value
            if reason:
                appointment.outcome_notes = reason
            appointment.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(appointment)
            
            return appointment
        finally:
            db.close()
    
    def get_appointments_by_campaign(self, campaign_id: int) -> List[Appointment]:
        """Get appointments by campaign"""
        db = self._get_db()
        try:
            return db.query(Appointment).filter(Appointment.campaign_id == campaign_id).all()
        finally:
            db.close()
    
    def get_appointments_by_persona(self, persona_id: int) -> List[Appointment]:
        """Get appointments by persona"""
        db = self._get_db()
        try:
            return db.query(Appointment).filter(Appointment.persona_id == persona_id).all()
        finally:
            db.close()
    
    def get_upcoming_appointments(self, days_ahead: int = 7) -> List[Appointment]:
        """Get upcoming appointments"""
        db = self._get_db()
        try:
            now = datetime.utcnow()
            end_date = now + timedelta(days=days_ahead)
            
            return db.query(Appointment).filter(
                Appointment.scheduled_at >= now,
                Appointment.scheduled_at <= end_date,
                Appointment.status.in_([
                    AppointmentStatus.PENDING.value,
                    AppointmentStatus.CONFIRMED.value,
                    AppointmentStatus.RESCHEDULED.value
                ])
            ).order_by(Appointment.scheduled_at).all()
        finally:
            db.close()
    
    def get_appointment_by_id(self, appointment_id: int) -> Optional[Appointment]:
        """Get appointment by ID"""
        db = self._get_db()
        try:
            return db.query(Appointment).filter(Appointment.id == appointment_id).first()
        finally:
            db.close()
    
    def get_appointment_statistics(self, campaign_id: Optional[int] = None) -> Dict:
        """Get appointment statistics"""
        db = self._get_db()
        try:
            if campaign_id:
                appointments = db.query(Appointment).filter(Appointment.campaign_id == campaign_id).all()
            else:
                appointments = db.query(Appointment).all()
            
            return {
                "total_appointments": len(appointments),
                "pending": len([a for a in appointments if a.status == AppointmentStatus.PENDING.value]),
                "confirmed": len([a for a in appointments if a.status == AppointmentStatus.CONFIRMED.value]),
                "completed": len([a for a in appointments if a.status == AppointmentStatus.COMPLETED.value]),
                "cancelled": len([a for a in appointments if a.status == AppointmentStatus.CANCELLED.value]),
                "rescheduled": len([a for a in appointments if a.status == AppointmentStatus.RESCHEDULED.value]),
            }
        finally:
            db.close()


***REMOVED*** Global instance
appointment_service = AppointmentService()

