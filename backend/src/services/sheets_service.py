"""
SERVICE: sheets_service
PURPOSE: Google Sheets integration for real-time data export
ENCODING: UTF-8 WITHOUT BOM
"""

import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

try:
    from google.oauth2.credentials import Credentials
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    SHEETS_AVAILABLE = True
except ImportError:
    SHEETS_AVAILABLE = False


class SheetsService:
    """
    Service for exporting data to Google Sheets in real-time.
    """
    
    def __init__(self):
        """Initialize Sheets Service."""
        self.service = None
        self.credentials = None
        
        # Try to get credentials
        credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
        service_account_email = os.getenv("GOOGLE_SHEETS_SERVICE_ACCOUNT_EMAIL")
        private_key = os.getenv("GOOGLE_SHEETS_PRIVATE_KEY")
        
        if SHEETS_AVAILABLE:
            try:
                if credentials_path and os.path.exists(credentials_path):
                    # Use service account JSON file
                    self.credentials = service_account.Credentials.from_service_account_file(
                        credentials_path,
                        scopes=['https://www.googleapis.com/auth/spreadsheets']
                    )
                elif service_account_email and private_key:
                    # Use service account credentials from env vars
                    from google.oauth2 import service_account
                    import json
                    creds_dict = {
                        "type": "service_account",
                        "project_id": os.getenv("GOOGLE_CLOUD_PROJECT_ID", ""),
                        "private_key_id": os.getenv("GOOGLE_SHEETS_PRIVATE_KEY_ID", ""),
                        "private_key": private_key.replace('\\n', '\n'),
                        "client_email": service_account_email,
                        "client_id": os.getenv("GOOGLE_SHEETS_CLIENT_ID", ""),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                    }
                    self.credentials = service_account.Credentials.from_service_account_info(
                        creds_dict,
                        scopes=['https://www.googleapis.com/auth/spreadsheets']
                    )
                else:
                    # Try Application Default Credentials
                    from google.auth import default
                    self.credentials, _ = default(scopes=['https://www.googleapis.com/auth/spreadsheets'])
                
                if self.credentials:
                    self.service = build('sheets', 'v4', credentials=self.credentials)
            except Exception as e:
                print(f"Warning: Could not initialize Sheets service: {e}")
                self.service = None
    
    def is_available(self) -> bool:
        """Check if Google Sheets API is available and configured."""
        return SHEETS_AVAILABLE and self.service is not None
    
    def create_spreadsheet(self, title: str) -> Dict[str, Any]:
        """
        Create a new Google Sheets spreadsheet.
        
        Args:
            title: Title of the spreadsheet
        
        Returns:
            Dictionary with spreadsheet ID and URL
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Google Sheets API is not available. Please configure credentials."
            }
        
        try:
            spreadsheet = {
                'properties': {
                    'title': title
                }
            }
            
            spreadsheet = self.service.spreadsheets().create(body=spreadsheet).execute()
            
            spreadsheet_id = spreadsheet.get('spreadsheetId')
            spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
            
            return {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "spreadsheet_url": spreadsheet_url,
                "title": title
            }
        except HttpError as e:
            return {
                "success": False,
                "error": f"Error creating spreadsheet: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def write_records_to_sheet(
        self,
        spreadsheet_id: str,
        records: List[Dict[str, Any]],
        sheet_name: str = "Discovery Records"
    ) -> Dict[str, Any]:
        """
        Write discovery records to a Google Sheets spreadsheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            records: List of record dictionaries
            sheet_name: Name of the sheet to write to
        
        Returns:
            Dictionary with success status and URL
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Google Sheets API is not available"
            }
        
        try:
            # Prepare headers
            headers = [
                "Record ID", "Company Name", "Address", "Website", "Phone", "Email",
                "Source", "Status", "Industry", "Employee Count", "Technology Stack",
                "Business Activity", "Created At", "Updated At"
            ]
            
            # Prepare data rows
            rows = [headers]
            for record in records:
                row = [
                    record.get("id") or record.get("record_id", ""),
                    record.get("name") or record.get("company_name", ""),
                    record.get("address", ""),
                    record.get("website", ""),
                    record.get("phone", ""),
                    record.get("email", ""),
                    record.get("source", ""),
                    record.get("status", ""),
                    record.get("industry", ""),
                    record.get("employee_count", ""),
                    ", ".join(record.get("technology_stack", [])) if isinstance(record.get("technology_stack"), list) else str(record.get("technology_stack", "")),
                    record.get("business_activity", ""),
                    record.get("created_at", ""),
                    datetime.utcnow().isoformat()
                ]
                rows.append(row)
            
            # Create or get sheet
            try:
                # Try to get existing sheet
                spreadsheet = self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
                sheet_exists = any(sheet['properties']['title'] == sheet_name for sheet in spreadsheet.get('sheets', []))
                
                if not sheet_exists:
                    # Create new sheet
                    request_body = {
                        'requests': [{
                            'addSheet': {
                                'properties': {
                                    'title': sheet_name
                                }
                            }
                        }]
                    }
                    self.service.spreadsheets().batchUpdate(
                        spreadsheetId=spreadsheet_id,
                        body=request_body
                    ).execute()
            except HttpError:
                pass
            
            # Write data
            range_name = f"{sheet_name}!A1"
            body = {
                'values': rows
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
            
            return {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "spreadsheet_url": spreadsheet_url,
                "rows_written": result.get('updatedRows', len(rows)),
                "sheet_name": sheet_name
            }
            
        except HttpError as e:
            return {
                "success": False,
                "error": f"Google Sheets API error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error writing to sheet: {str(e)}"
            }
    
    def create_and_write_records(
        self,
        records: List[Dict[str, Any]],
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new spreadsheet and write records to it.
        
        Args:
            records: List of record dictionaries
            title: Title for the spreadsheet (default: "FinderOS Discovery Records - {timestamp}")
        
        Returns:
            Dictionary with spreadsheet URL and details
        """
        if not title:
            title = f"FinderOS Discovery Records - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Create spreadsheet
        create_result = self.create_spreadsheet(title)
        if not create_result.get("success"):
            return create_result
        
        spreadsheet_id = create_result.get("spreadsheet_id")
        
        # Write records
        write_result = self.write_records_to_sheet(spreadsheet_id, records)
        if not write_result.get("success"):
            return write_result
        
        return {
            "success": True,
            "spreadsheet_id": spreadsheet_id,
            "spreadsheet_url": write_result.get("spreadsheet_url"),
            "title": title,
            "rows_written": write_result.get("rows_written", 0),
            "sheet_name": write_result.get("sheet_name", "Discovery Records")
        }


# Singleton instance
_sheets_service_instance = None


def get_sheets_service() -> SheetsService:
    """Get or create SheetsService singleton instance."""
    global _sheets_service_instance
    if _sheets_service_instance is None:
        _sheets_service_instance = SheetsService()
    return _sheets_service_instance


