"""
SERVICE: notification_service
PURPOSE: Notification service for browser and email notifications
ENCODING: UTF-8 WITHOUT BOM
"""

import os
import logging
import smtplib
from typing import Dict, Optional, Any, List
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session

from src.config.settings import get_int_env
from src.models.notification import Notification
from src.models.user import User

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for sending notifications to users.
    Supports browser notifications and email notifications.
    """
    
    def __init__(self, db: Session):
        """Initialize Notification Service with database session."""
        self.db = db
        
        # Email configuration
        self.smtp_host = os.getenv("SMTP_HOST") or "smtp.gmail.com"
        self.smtp_port = get_int_env("SMTP_PORT", 587)
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.smtp_from_email = os.getenv("SMTP_FROM_EMAIL", self.smtp_user)
        self.smtp_from_name = os.getenv("SMTP_FROM_NAME", "FinderOS")
        
        # Check if email is configured
        self.email_enabled = bool(self.smtp_user and self.smtp_password)
    
    def create_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        notification_type: str = "system",
        metadata: Optional[Dict[str, Any]] = None,
        action_url: Optional[str] = None,
        send_browser: bool = True,
        send_email: bool = False
    ) -> Dict[str, Any]:
        """
        Create a notification for a user.
        
        Args:
            user_id: User ID
            title: Notification title
            message: Notification message
            notification_type: Type of notification (appointment, lead, campaign, system)
            metadata: Additional metadata
            action_url: URL to navigate when notification is clicked
            send_browser: Whether to send browser notification
            send_email: Whether to send email notification
        
        Returns:
            Dictionary with notification creation result
        """
        try:
            # Create notification record
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type,
                metadata=metadata or {},
                action_url=action_url,
                browser_notification_sent=send_browser,
                email_notification_sent=False   # Will be updated after sending
            )
            
            self.db.add(notification)
            self.db.commit()
            self.db.refresh(notification)
            
            # Send browser notification (if enabled)
            if send_browser:
                # Browser notifications are handled by frontend
                # We just mark it as sent
                pass
            
            # Send email notification (if enabled)
            if send_email and self.email_enabled:
                user = self.db.query(User).filter(User.id == user_id).first()
                if user and user.email:
                    email_sent = self._send_email_notification(
                        to_email=user.email,
                        to_name=user.full_name or user.email,
                        title=title,
                        message=message,
                        action_url=action_url
                    )
                    
                    if email_sent:
                        notification.email_notification_sent = True
                        self.db.commit()
            
            logger.info(f"Notification created: {notification.id} for user {user_id}")
            
            return {
                "success": True,
                "notification": notification.to_dict(),
                "message": "Notification created successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating notification: {str(e)}")
            return {
                "success": False,
                "error": f"Error creating notification: {str(e)}"
            }
    
    def notify_new_appointment(
        self,
        user_id: int,
        appointment_id: int,
        lead_name: str,
        scheduled_at: datetime,
        meet_link: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send notification for a new appointment.
        
        Args:
            user_id: User ID
            appointment_id: Appointment ID
            lead_name: Lead's name
            scheduled_at: Appointment scheduled time
            meet_link: Google Meet link (optional)
        
        Returns:
            Dictionary with notification result
        """
        scheduled_str = scheduled_at.strftime("%B %d, %Y at %I:%M %p")
        
        title = "🎉 New Appointment Scheduled!"
        message = f"You have a new appointment with {lead_name} scheduled for {scheduled_str}."
        
        if meet_link:
            message += f"\n\nJoin Google Meet: {meet_link}"
        
        return self.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type="appointment",
            metadata={
                "appointment_id": appointment_id,
                "lead_name": lead_name,
                "scheduled_at": scheduled_at.isoformat(),
                "meet_link": meet_link
            },
            action_url=f"/ui/finder_os_dashboard.html#tab-11",
            send_browser=True,
            send_email=True   # Send email for important notifications
        )
    
    def notify_new_lead(
        self,
        user_id: int,
        lead_id: int,
        lead_name: str,
        lead_email: str
    ) -> Dict[str, Any]:
        """
        Send notification for a new lead from Google Ads.
        
        Args:
            user_id: User ID
            lead_id: Lead ID
            lead_name: Lead's name
            lead_email: Lead's email
        
        Returns:
            Dictionary with notification result
        """
        title = "📥 New Lead from Google Ads!"
        message = f"New lead received: {lead_name} ({lead_email}). An appointment has been automatically scheduled."
        
        return self.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type="lead",
            metadata={
                "lead_id": lead_id,
                "lead_name": lead_name,
                "lead_email": lead_email
            },
            action_url=f"/ui/finder_os_dashboard.html#tab-11",
            send_browser=True,
            send_email=True
        )
    
    def notify_campaign_status(
        self,
        user_id: int,
        campaign_id: int,
        campaign_name: str,
        status: str,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send notification for campaign status changes.
        
        Args:
            user_id: User ID
            campaign_id: Campaign ID
            campaign_name: Campaign name
            status: Campaign status
            message: Custom message (optional)
        
        Returns:
            Dictionary with notification result
        """
        title = f"📊 Campaign Update: {campaign_name}"
        notification_message = message or f"Your campaign '{campaign_name}' status changed to: {status}"
        
        return self.create_notification(
            user_id=user_id,
            title=title,
            message=notification_message,
            notification_type="campaign",
            metadata={
                "campaign_id": campaign_id,
                "campaign_name": campaign_name,
                "status": status
            },
            action_url=f"/ui/finder_os_dashboard.html#tab-9",
            send_browser=True,
            send_email=False   # Don't send email for campaign updates
        )
    
    def _send_email_notification(
        self,
        to_email: str,
        to_name: str,
        title: str,
        message: str,
        action_url: Optional[str] = None
    ) -> bool:
        """
        Send email notification.
        
        Args:
            to_email: Recipient email
            to_name: Recipient name
            title: Email subject
            message: Email body
            action_url: Optional action URL
        
        Returns:
            True if email sent successfully
        """
        if not self.email_enabled:
            logger.warning("Email notifications not configured")
            return False
        
        try:
            # Create email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = title
            msg['From'] = f"{self.smtp_from_name} <{self.smtp_from_email}>"
            msg['To'] = to_email
            
            # Create HTML email body
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color:  #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color:  #667eea;">{title}</h2>
                        <p>{message.replace(chr(10), '<br>')}</p>
                        {f'<p><a href="{action_url}" style="background:  #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">View Details</a></p>' if action_url else ''}
                        <hr style="border: none; border-top: 1px solid  #e5e7eb; margin: 20px 0;">
                        <p style="color:  #6b7280; font-size: 12px;">This is an automated notification from FinderOS.</p>
                    </div>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email notification sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
            return False
    
    def get_user_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get notifications for a user.
        
        Args:
            user_id: User ID
            unread_only: Only return unread notifications
            limit: Maximum number of notifications to return
        
        Returns:
            List of notification dictionaries
        """
        try:
            query = self.db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.is_archived == False
            )
            
            if unread_only:
                query = query.filter(Notification.is_read == False)
            
            notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()
            
            return [notification.to_dict() for notification in notifications]
            
        except Exception as e:
            logger.error(f"Error getting notifications: {str(e)}")
            return []
    
    def mark_notification_read(
        self,
        notification_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Mark a notification as read.
        
        Args:
            notification_id: Notification ID
            user_id: User ID (for security)
        
        Returns:
            Dictionary with result
        """
        try:
            notification = self.db.query(Notification).filter(
                Notification.id == notification_id,
                Notification.user_id == user_id
            ).first()
            
            if not notification:
                return {
                    "success": False,
                    "error": "Notification not found"
                }
            
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            self.db.commit()
            
            return {
                "success": True,
                "message": "Notification marked as read"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error marking notification as read: {str(e)}")
            return {
                "success": False,
                "error": f"Error: {str(e)}"
            }


def get_notification_service(db: Session) -> NotificationService:
    """
    Get NotificationService instance with database session.
    """
    return NotificationService(db)


