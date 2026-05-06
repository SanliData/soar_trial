"""
SERVICES: __init__
PURPOSE: Export all services
ENCODING: UTF-8 WITHOUT BOM
"""

from src.services.auth_service import AuthService, get_auth_service
from src.services.vision_service import VisionService, get_vision_service
from src.services.web_research_service import WebResearchService, get_web_research_service
from src.services.gemini_analysis_service import GeminiAnalysisService, get_gemini_analysis_service
from src.services.company_intelligence_service import CompanyIntelligenceService, get_company_intelligence_service
from src.services.bigquery_service import BigQueryService, get_bigquery_service
from src.services.sheets_service import SheetsService, get_sheets_service
from src.services.background_tasks import BackgroundTaskManager, get_background_task_manager, start_background_tasks, stop_background_tasks
from src.services.google_ads_service import GoogleAdsService, get_google_ads_service
from src.services.calendar_service import CalendarService, get_calendar_service
from src.services.lead_service import LeadService, get_lead_service
from src.services.notification_service import NotificationService, get_notification_service
from src.services.error_logging_service import ErrorLoggingService, get_error_logging_service

__all__ = [
    "AuthService",
    "get_auth_service",
    "VisionService",
    "get_vision_service",
    "WebResearchService",
    "get_web_research_service",
    "GeminiAnalysisService",
    "get_gemini_analysis_service",
    "CompanyIntelligenceService",
    "get_company_intelligence_service",
    "BigQueryService",
    "get_bigquery_service",
    "SheetsService",
    "get_sheets_service",
    "BackgroundTaskManager",
    "get_background_task_manager",
    "start_background_tasks",
    "stop_background_tasks",
    "GoogleAdsService",
    "get_google_ads_service",
    "CalendarService",
    "get_calendar_service",
    "LeadService",
    "get_lead_service",
    "NotificationService",
    "get_notification_service",
    "ErrorLoggingService",
    "get_error_logging_service"
]
