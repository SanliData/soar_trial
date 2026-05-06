"""
SERVICE: calendar_service
PURPOSE: Google Calendar API integration for appointment scheduling
ENCODING: UTF-8 WITHOUT BOM
"""

import os
import logging
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

try:
    from google.oauth2 import service_account
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False
    service_account = None


class CalendarService:
    """
    Service for Google Calendar API integration.
    Handles availability checking, event creation, and Google Meet integration.
    """
    
    def __init__(self):
        """Initialize Calendar Service with configuration from environment variables."""
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GOOGLE_CALENDAR_REDIRECT_URI", "http://localhost:8000/v1/calendar/oauth/callback")
        self.scopes = [
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/calendar.events'
        ]
        self.service = None
    
    def _get_credentials(self, user_email: Optional[str] = None) -> Optional[Credentials]:
        """
        Get Google Calendar credentials for a user.
        Uses OAuth2 flow or service account.
        
        Args:
            user_email: User's email address (for OAuth2)
        
        Returns:
            Google Credentials object or None
        """
        if not CALENDAR_AVAILABLE:
            logger.error("Google Calendar API libraries not installed")
            return None
        
        try:
            ***REMOVED*** Option 1: Service Account (for server-to-server)
            service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
            if service_account_file and os.path.exists(service_account_file):
                credentials = service_account.Credentials.from_service_account_file(
                    service_account_file,
                    scopes=self.scopes
                )
                logger.info("Using service account credentials")
                return credentials
            
            ***REMOVED*** Option 2: OAuth2 (for user-specific access)
            ***REMOVED*** In production, store refresh tokens per user
            refresh_token = os.getenv("GOOGLE_CALENDAR_REFRESH_TOKEN")
            if refresh_token and self.client_id and self.client_secret:
                credentials = Credentials(
                    token=None,
                    refresh_token=refresh_token,
                    token_uri='https://oauth2.googleapis.com/token',
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    scopes=self.scopes
                )
                
                ***REMOVED*** Refresh token if needed
                if credentials.expired:
                    credentials.refresh(Request())
                
                logger.info("Using OAuth2 credentials")
                return credentials
            
            logger.warning("No Google Calendar credentials configured")
            return None
            
        except Exception as e:
            logger.error(f"Error getting credentials: {str(e)}")
            return None
    
    def _get_calendar_service(self, user_email: Optional[str] = None):
        """
        Get Google Calendar API service instance.
        
        Args:
            user_email: User's email address
        
        Returns:
            Calendar service instance or None
        """
        if self.service:
            return self.service
        
        credentials = self._get_credentials(user_email)
        if not credentials:
            return None
        
        try:
            self.service = build('calendar', 'v3', credentials=credentials)
            return self.service
        except Exception as e:
            logger.error(f"Error building calendar service: {str(e)}")
            return None
    
    def check_availability(
        self,
        user_email: str,
        start_time: datetime,
        end_time: datetime,
        calendar_id: str = 'primary'
    ) -> Dict[str, Any]:
        """
        Check user's calendar availability for a time slot.
        
        Args:
            user_email: User's email address
            start_time: Start time of the slot
            end_time: End time of the slot
            calendar_id: Calendar ID (default: 'primary')
        
        Returns:
            Dictionary with availability status
        """
        if not CALENDAR_AVAILABLE:
            return {
                "success": False,
                "error": "Google Calendar API not available"
            }
        
        try:
            service = self._get_calendar_service(user_email)
            if not service:
                return {
                    "success": False,
                    "error": "Failed to get calendar service"
                }
            
            ***REMOVED*** Query for existing events in the time range
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=start_time.isoformat() + 'Z',
                timeMax=end_time.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            ***REMOVED*** Check if there are any conflicting events
            is_available = len(events) == 0
            
            return {
                "success": True,
                "available": is_available,
                "conflicting_events": len(events),
                "events": [
                    {
                        "summary": event.get('summary', 'No Title'),
                        "start": event.get('start', {}).get('dateTime', event.get('start', {}).get('date')),
                        "end": event.get('end', {}).get('dateTime', event.get('end', {}).get('date'))
                    }
                    for event in events
                ],
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            }
            
        except HttpError as e:
            logger.error(f"Google Calendar API error: {str(e)}")
            return {
                "success": False,
                "error": f"Google Calendar API error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error checking availability: {str(e)}")
            return {
                "success": False,
                "error": f"Error: {str(e)}"
            }
    
    def find_available_slots(
        self,
        user_email: str,
        date: datetime,
        duration_minutes: int = 30,
        start_hour: int = 9,
        end_hour: int = 17,
        calendar_id: str = 'primary'
    ) -> Dict[str, Any]:
        """
        Find available time slots for a given date.
        
        Args:
            user_email: User's email address
            date: Date to check (datetime object, time will be ignored)
            duration_minutes: Duration of each slot in minutes
            start_hour: Start hour (default: 9 AM)
            end_hour: End hour (default: 5 PM)
            calendar_id: Calendar ID (default: 'primary')
        
        Returns:
            Dictionary with available time slots
        """
        if not CALENDAR_AVAILABLE:
            return {
                "success": False,
                "error": "Google Calendar API not available"
            }
        
        try:
            service = self._get_calendar_service(user_email)
            if not service:
                return {
                    "success": False,
                    "error": "Failed to get calendar service"
                }
            
            ***REMOVED*** Set date boundaries
            start_of_day = date.replace(hour=start_hour, minute=0, second=0, microsecond=0)
            end_of_day = date.replace(hour=end_hour, minute=0, second=0, microsecond=0)
            
            ***REMOVED*** Get all events for the day
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=start_of_day.isoformat() + 'Z',
                timeMax=end_of_day.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            ***REMOVED*** Generate potential slots (every 30 minutes)
            slot_duration = timedelta(minutes=duration_minutes)
            slot_interval = timedelta(minutes=30)
            current_time = start_of_day
            available_slots = []
            
            while current_time + slot_duration <= end_of_day:
                slot_end = current_time + slot_duration
                
                ***REMOVED*** Check if this slot conflicts with any event
                is_available = True
                for event in events:
                    event_start_str = event.get('start', {}).get('dateTime', event.get('start', {}).get('date'))
                    event_end_str = event.get('end', {}).get('dateTime', event.get('end', {}).get('date'))
                    
                    if event_start_str:
                        event_start = datetime.fromisoformat(event_start_str.replace('Z', '+00:00'))
                        event_end = datetime.fromisoformat(event_end_str.replace('Z', '+00:00'))
                        
                        ***REMOVED*** Check for overlap
                        if not (slot_end <= event_start or current_time >= event_end):
                            is_available = False
                            break
                
                if is_available:
                    available_slots.append({
                        "start": current_time.isoformat(),
                        "end": slot_end.isoformat(),
                        "duration_minutes": duration_minutes
                    })
                
                current_time += slot_interval
            
            return {
                "success": True,
                "date": date.date().isoformat(),
                "available_slots": available_slots,
                "total_slots": len(available_slots),
                "duration_minutes": duration_minutes
            }
            
        except HttpError as e:
            logger.error(f"Google Calendar API error: {str(e)}")
            return {
                "success": False,
                "error": f"Google Calendar API error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error finding available slots: {str(e)}")
            return {
                "success": False,
                "error": f"Error: {str(e)}"
            }
    
    def create_appointment_event(
        self,
        user_email: str,
        lead_email: str,
        lead_name: str,
        start_time: datetime,
        duration_minutes: int = 30,
        title: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        create_google_meet: bool = True,
        calendar_id: str = 'primary'
    ) -> Dict[str, Any]:
        """
        Create a Google Calendar event for an appointment with Google Meet link.
        Lead's email is added as an attendee.
        
        Args:
            user_email: Calendar owner's email (FinderOS user)
            lead_email: Lead's email address (from Lead Form)
            lead_name: Lead's full name
            start_time: Appointment start time
            duration_minutes: Appointment duration
            title: Event title (default: "Meeting with {Lead Name}")
            description: Event description
            location: Event location (default: "Google Meet")
            create_google_meet: Whether to create Google Meet link
            calendar_id: Calendar ID (default: 'primary')
        
        Returns:
            Dictionary with event creation result
        """
        if not CALENDAR_AVAILABLE:
            return {
                "success": False,
                "error": "Google Calendar API not available"
            }
        
        try:
            service = self._get_calendar_service(user_email)
            if not service:
                return {
                    "success": False,
                    "error": "Failed to get calendar service"
                }
            
            ***REMOVED*** Calculate end time
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            ***REMOVED*** Set default title
            if not title:
                title = f"Meeting with {lead_name}"
            
            ***REMOVED*** Set default description
            if not description:
                description = f"Follow-up meeting with {lead_name} ({lead_email})"
            
            ***REMOVED*** Build event
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'attendees': [
                    {'email': lead_email, 'displayName': lead_name},
                    {'email': user_email}  ***REMOVED*** Calendar owner
                ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  ***REMOVED*** 1 day before
                        {'method': 'popup', 'minutes': 15},  ***REMOVED*** 15 minutes before
                    ],
                },
            }
            
            ***REMOVED*** Add Google Meet link if requested
            if create_google_meet:
                event['conferenceData'] = {
                    'createRequest': {
                        'requestId': f"meet-{start_time.timestamp()}",
                        'conferenceSolutionKey': {
                            'type': 'hangoutsMeet'
                        }
                    }
                }
            
            ***REMOVED*** Add location if provided
            if location:
                event['location'] = location
            elif create_google_meet:
                event['location'] = 'Google Meet'  ***REMOVED*** Will be updated with actual link
            
            ***REMOVED*** Create event
            created_event = service.events().insert(
                calendarId=calendar_id,
                body=event,
                conferenceDataVersion=1 if create_google_meet else 0,
                sendUpdates='all'  ***REMOVED*** Send invitations to all attendees
            ).execute()
            
            ***REMOVED*** Extract Google Meet link if created
            meet_link = None
            if create_google_meet and 'conferenceData' in created_event:
                meet_link = created_event['conferenceData'].get('entryPoints', [{}])[0].get('uri')
                if not meet_link:
                    ***REMOVED*** Fallback: check hangoutLink
                    meet_link = created_event.get('hangoutLink')
            
            logger.info(f"Calendar event created: {created_event.get('id')} for {lead_email}")
            
            return {
                "success": True,
                "event_id": created_event.get('id'),
                "event_link": created_event.get('htmlLink'),
                "meet_link": meet_link,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "attendees": [
                    attendee.get('email')
                    for attendee in created_event.get('attendees', [])
                ],
                "event": {
                    "id": created_event.get('id'),
                    "summary": created_event.get('summary'),
                    "description": created_event.get('description'),
                    "start": created_event.get('start'),
                    "end": created_event.get('end'),
                    "location": created_event.get('location'),
                    "htmlLink": created_event.get('htmlLink')
                }
            }
            
        except HttpError as e:
            logger.error(f"Google Calendar API error: {str(e)}")
            return {
                "success": False,
                "error": f"Google Calendar API error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error creating calendar event: {str(e)}")
            return {
                "success": False,
                "error": f"Error: {str(e)}"
            }
    
    def update_appointment_event(
        self,
        user_email: str,
        event_id: str,
        start_time: Optional[datetime] = None,
        duration_minutes: Optional[int] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        calendar_id: str = 'primary'
    ) -> Dict[str, Any]:
        """
        Update an existing calendar event.
        
        Args:
            user_email: Calendar owner's email
            event_id: Google Calendar event ID
            start_time: New start time (optional)
            duration_minutes: New duration (optional)
            title: New title (optional)
            description: New description (optional)
            calendar_id: Calendar ID (default: 'primary')
        
        Returns:
            Dictionary with update result
        """
        if not CALENDAR_AVAILABLE:
            return {
                "success": False,
                "error": "Google Calendar API not available"
            }
        
        try:
            service = self._get_calendar_service(user_email)
            if not service:
                return {
                    "success": False,
                    "error": "Failed to get calendar service"
                }
            
            ***REMOVED*** Get existing event
            event = service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            ***REMOVED*** Update fields
            if start_time:
                event['start']['dateTime'] = start_time.isoformat()
                if duration_minutes:
                    end_time = start_time + timedelta(minutes=duration_minutes)
                    event['end']['dateTime'] = end_time.isoformat()
            
            if title:
                event['summary'] = title
            
            if description:
                event['description'] = description
            
            ***REMOVED*** Update event
            updated_event = service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event,
                sendUpdates='all'
            ).execute()
            
            logger.info(f"Calendar event updated: {event_id}")
            
            return {
                "success": True,
                "event_id": updated_event.get('id'),
                "event_link": updated_event.get('htmlLink'),
                "message": "Event updated successfully"
            }
            
        except HttpError as e:
            logger.error(f"Google Calendar API error: {str(e)}")
            return {
                "success": False,
                "error": f"Google Calendar API error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error updating calendar event: {str(e)}")
            return {
                "success": False,
                "error": f"Error: {str(e)}"
            }
    
    def delete_appointment_event(
        self,
        user_email: str,
        event_id: str,
        calendar_id: str = 'primary'
    ) -> Dict[str, Any]:
        """
        Delete a calendar event.
        
        Args:
            user_email: Calendar owner's email
            event_id: Google Calendar event ID
            calendar_id: Calendar ID (default: 'primary')
        
        Returns:
            Dictionary with deletion result
        """
        if not CALENDAR_AVAILABLE:
            return {
                "success": False,
                "error": "Google Calendar API not available"
            }
        
        try:
            service = self._get_calendar_service(user_email)
            if not service:
                return {
                    "success": False,
                    "error": "Failed to get calendar service"
                }
            
            service.events().delete(
                calendarId=calendar_id,
                eventId=event_id,
                sendUpdates='all'
            ).execute()
            
            logger.info(f"Calendar event deleted: {event_id}")
            
            return {
                "success": True,
                "message": "Event deleted successfully"
            }
            
        except HttpError as e:
            logger.error(f"Google Calendar API error: {str(e)}")
            return {
                "success": False,
                "error": f"Google Calendar API error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error deleting calendar event: {str(e)}")
            return {
                "success": False,
                "error": f"Error: {str(e)}"
            }


***REMOVED*** Singleton instance
_calendar_service = None


def get_calendar_service() -> CalendarService:
    """
    Get singleton instance of CalendarService.
    """
    global _calendar_service
    if _calendar_service is None:
        _calendar_service = CalendarService()
    return _calendar_service


