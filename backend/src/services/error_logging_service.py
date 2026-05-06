"""
SERVICE: error_logging_service
PURPOSE: Comprehensive error logging for production debugging
ENCODING: UTF-8 WITHOUT BOM
"""

import logging
import traceback
import sys
from typing import Dict, Optional, Any, List
from datetime import datetime
from sqlalchemy.orm import Session

from src.models.error_log import ErrorLog

logger = logging.getLogger(__name__)


class ErrorLoggingService:
    """
    Service for logging errors to database for production debugging.
    Captures exceptions, context, and request information.
    """
    
    def __init__(self, db: Session):
        """Initialize Error Logging Service with database session."""
        self.db = db
    
    def log_error(
        self,
        error: Exception,
        service_name: Optional[str] = None,
        endpoint: Optional[str] = None,
        http_method: Optional[str] = None,
        request_data: Optional[Dict[str, Any]] = None,
        request_headers: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None,
        severity: str = "error",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log an error to the database.
        
        Args:
            error: Exception object
            service_name: Name of the service where error occurred
            endpoint: API endpoint (if applicable)
            http_method: HTTP method (GET, POST, etc.)
            request_data: Request payload/parameters
            request_headers: Request headers (will be sanitized)
            user_id: User ID (if applicable)
            severity: Error severity (info, warning, error, critical)
            metadata: Additional metadata
        
        Returns:
            Dictionary with error log creation result
        """
        try:
            # Get error information
            error_type = type(error).__name__
            error_message = str(error)
            error_traceback = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
            
            # Sanitize headers (remove sensitive information)
            sanitized_headers = self._sanitize_headers(request_headers) if request_headers else None
            
            # Create error log
            error_log = ErrorLog(
                user_id=user_id,
                error_type=error_type,
                error_message=error_message,
                error_traceback=error_traceback,
                service_name=service_name,
                endpoint=endpoint,
                http_method=http_method,
                request_data=request_data,
                request_headers=sanitized_headers,
                severity=severity,
                metadata=metadata or {}
            )
            
            self.db.add(error_log)
            self.db.commit()
            self.db.refresh(error_log)
            
            # Also log to standard logger
            logger.error(f"Error logged to database: {error_log.id} - {error_type}: {error_message}")
            
            return {
                "success": True,
                "error_log_id": error_log.id,
                "message": "Error logged successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            # Fallback to standard logging if database logging fails
            logger.error(f"Failed to log error to database: {str(e)}")
            logger.error(f"Original error: {error_type}: {error_message}")
            return {
                "success": False,
                "error": f"Failed to log error: {str(e)}"
            }
    
    def _sanitize_headers(self, headers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize request headers by removing sensitive information.
        
        Args:
            headers: Request headers dictionary
        
        Returns:
            Sanitized headers dictionary
        """
        sensitive_keys = ['authorization', 'cookie', 'x-api-key', 'password', 'secret', 'token']
        sanitized = {}
        
        for key, value in headers.items():
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in sensitive_keys):
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = value
        
        return sanitized
    
    def get_error_logs(
        self,
        service_name: Optional[str] = None,
        severity: Optional[str] = None,
        unresolved_only: bool = False,
        user_id: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get error logs with filters.
        
        Args:
            service_name: Filter by service name
            severity: Filter by severity
            unresolved_only: Only return unresolved errors
            user_id: Filter by user ID
            limit: Maximum number of logs to return
        
        Returns:
            List of error log dictionaries
        """
        try:
            query = self.db.query(ErrorLog)
            
            if service_name:
                query = query.filter(ErrorLog.service_name == service_name)
            
            if severity:
                query = query.filter(ErrorLog.severity == severity)
            
            if unresolved_only:
                query = query.filter(ErrorLog.is_resolved == False)
            
            if user_id:
                query = query.filter(ErrorLog.user_id == user_id)
            
            error_logs = query.order_by(ErrorLog.created_at.desc()).limit(limit).all()
            
            return [error_log.to_dict() for error_log in error_logs]
            
        except Exception as e:
            logger.error(f"Error getting error logs: {str(e)}")
            return []
    
    def mark_error_resolved(
        self,
        error_log_id: int,
        resolution_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Mark an error as resolved.
        
        Args:
            error_log_id: Error log ID
            resolution_notes: Notes about the resolution
        
        Returns:
            Dictionary with result
        """
        try:
            error_log = self.db.query(ErrorLog).filter(ErrorLog.id == error_log_id).first()
            
            if not error_log:
                return {
                    "success": False,
                    "error": "Error log not found"
                }
            
            error_log.is_resolved = True
            error_log.resolved_at = datetime.utcnow()
            error_log.resolution_notes = resolution_notes
            
            self.db.commit()
            
            return {
                "success": True,
                "message": "Error marked as resolved"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error marking error as resolved: {str(e)}")
            return {
                "success": False,
                "error": f"Error: {str(e)}"
            }
    
    def get_error_statistics(
        self,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get error statistics for the last N days.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Dictionary with error statistics
        """
        try:
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Total errors
            total_errors = self.db.query(ErrorLog).filter(
                ErrorLog.created_at >= cutoff_date
            ).count()
            
            # Errors by severity
            errors_by_severity = {}
            for severity in ['info', 'warning', 'error', 'critical']:
                count = self.db.query(ErrorLog).filter(
                    ErrorLog.created_at >= cutoff_date,
                    ErrorLog.severity == severity
                ).count()
                errors_by_severity[severity] = count
            
            # Errors by service
            errors_by_service = {}
            services = self.db.query(ErrorLog.service_name).filter(
                ErrorLog.created_at >= cutoff_date,
                ErrorLog.service_name.isnot(None)
            ).distinct().all()
            
            for service_tuple in services:
                service = service_tuple[0]
                count = self.db.query(ErrorLog).filter(
                    ErrorLog.created_at >= cutoff_date,
                    ErrorLog.service_name == service
                ).count()
                errors_by_service[service] = count
            
            # Unresolved errors
            unresolved_count = self.db.query(ErrorLog).filter(
                ErrorLog.created_at >= cutoff_date,
                ErrorLog.is_resolved == False
            ).count()
            
            return {
                "success": True,
                "period_days": days,
                "total_errors": total_errors,
                "errors_by_severity": errors_by_severity,
                "errors_by_service": errors_by_service,
                "unresolved_count": unresolved_count,
                "resolved_count": total_errors - unresolved_count
            }
            
        except Exception as e:
            logger.error(f"Error getting error statistics: {str(e)}")
            return {
                "success": False,
                "error": f"Error: {str(e)}"
            }


def get_error_logging_service(db: Session) -> ErrorLoggingService:
    """
    Get ErrorLoggingService instance with database session.
    """
    return ErrorLoggingService(db)


