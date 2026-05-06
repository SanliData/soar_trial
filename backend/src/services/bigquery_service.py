"""
SERVICE: bigquery_service
PURPOSE: Google BigQuery integration for analytics and data warehousing
ENCODING: UTF-8 WITHOUT BOM
"""

import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

try:
    from google.cloud import bigquery
    from google.cloud.exceptions import NotFound
    BIGQUERY_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False


class BigQueryService:
    """
    Service for exporting discovery records to Google BigQuery for analytics.
    """
    
    def __init__(self):
        """Initialize BigQuery Service."""
        self.client = None
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
        self.dataset_id = os.getenv("BIGQUERY_DATASET_ID", "finderos_analytics")
        self.table_id = os.getenv("BIGQUERY_TABLE_ID", "discovery_records")
        
        if BIGQUERY_AVAILABLE and self.project_id:
            try:
                self.client = bigquery.Client(project=self.project_id)
            except Exception as e:
                print(f"Warning: Could not initialize BigQuery client: {e}")
                self.client = None
    
    def is_available(self) -> bool:
        """Check if BigQuery is available and configured."""
        return BIGQUERY_AVAILABLE and self.client is not None
    
    def ensure_dataset_and_table(self) -> bool:
        """
        Ensure dataset and table exist in BigQuery.
        Creates them if they don't exist.
        """
        if not self.is_available():
            return False
        
        try:
            # Create dataset if it doesn't exist
            dataset_ref = self.client.dataset(self.dataset_id)
            try:
                self.client.get_dataset(dataset_ref)
            except NotFound:
                dataset = bigquery.Dataset(dataset_ref)
                dataset.location = os.getenv("BIGQUERY_LOCATION", "US")
                dataset.description = "FinderOS Discovery Records Analytics"
                self.client.create_dataset(dataset)
            
            # Create table if it doesn't exist
            table_ref = dataset_ref.table(self.table_id)
            try:
                self.client.get_table(table_ref)
            except NotFound:
                schema = [
                    bigquery.SchemaField("record_id", "STRING", mode="REQUIRED"),
                    bigquery.SchemaField("company_name", "STRING", mode="REQUIRED"),
                    bigquery.SchemaField("address", "STRING"),
                    bigquery.SchemaField("website", "STRING"),
                    bigquery.SchemaField("phone", "STRING"),
                    bigquery.SchemaField("email", "STRING"),
                    bigquery.SchemaField("source", "STRING"),
                    bigquery.SchemaField("status", "STRING"),
                    bigquery.SchemaField("industry", "STRING"),
                    bigquery.SchemaField("employee_count", "STRING"),
                    bigquery.SchemaField("technology_stack", "STRING", mode="REPEATED"),
                    bigquery.SchemaField("business_activity", "STRING"),
                    bigquery.SchemaField("intelligence_data", "JSON"),
                    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
                    bigquery.SchemaField("updated_at", "TIMESTAMP"),
                ]
                table = bigquery.Table(table_ref, schema=schema)
                table.description = "Discovery records from FinderOS"
                self.client.create_table(table)
            
            return True
        except Exception as e:
            print(f"Error ensuring dataset/table: {e}")
            return False
    
    def export_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Export a single discovery record to BigQuery.
        
        Args:
            record: Dictionary containing record data
        
        Returns:
            Dictionary with success status and error if any
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "BigQuery is not available. Please configure GOOGLE_CLOUD_PROJECT_ID."
            }
        
        if not self.ensure_dataset_and_table():
            return {
                "success": False,
                "error": "Could not ensure dataset and table exist"
            }
        
        try:
            # Prepare row data
            row = {
                "record_id": record.get("id") or record.get("record_id") or f"rec_{datetime.utcnow().timestamp()}",
                "company_name": record.get("name") or record.get("company_name", ""),
                "address": record.get("address", ""),
                "website": record.get("website", ""),
                "phone": record.get("phone", ""),
                "email": record.get("email", ""),
                "source": record.get("source", ""),
                "status": record.get("status", ""),
                "industry": record.get("industry", ""),
                "employee_count": record.get("employee_count", ""),
                "technology_stack": record.get("technology_stack", []) or [],
                "business_activity": record.get("business_activity", ""),
                "intelligence_data": json.dumps(record.get("intelligence", {})),
                "created_at": record.get("created_at") or datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
            
            # Insert row
            table_ref = self.client.dataset(self.dataset_id).table(self.table_id)
            errors = self.client.insert_rows_json(table_ref, [row])
            
            if errors:
                return {
                    "success": False,
                    "error": f"BigQuery insert errors: {errors}"
                }
            
            return {
                "success": True,
                "record_id": row["record_id"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error exporting to BigQuery: {str(e)}"
            }
    
    def batch_export_records(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Export multiple records to BigQuery in batch.
        
        Args:
            records: List of record dictionaries
        
        Returns:
            Dictionary with success status and results
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "BigQuery is not available"
            }
        
        if not self.ensure_dataset_and_table():
            return {
                "success": False,
                "error": "Could not ensure dataset and table exist"
            }
        
        try:
            rows = []
            for record in records:
                row = {
                    "record_id": record.get("id") or record.get("record_id") or f"rec_{datetime.utcnow().timestamp()}",
                    "company_name": record.get("name") or record.get("company_name", ""),
                    "address": record.get("address", ""),
                    "website": record.get("website", ""),
                    "phone": record.get("phone", ""),
                    "email": record.get("email", ""),
                    "source": record.get("source", ""),
                    "status": record.get("status", ""),
                    "industry": record.get("industry", ""),
                    "employee_count": record.get("employee_count", ""),
                    "technology_stack": record.get("technology_stack", []) or [],
                    "business_activity": record.get("business_activity", ""),
                    "intelligence_data": json.dumps(record.get("intelligence", {})),
                    "created_at": record.get("created_at") or datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                }
                rows.append(row)
            
            if not rows:
                return {
                    "success": False,
                    "error": "No records to export"
                }
            
            # Batch insert
            table_ref = self.client.dataset(self.dataset_id).table(self.table_id)
            errors = self.client.insert_rows_json(table_ref, rows)
            
            if errors:
                return {
                    "success": False,
                    "error": f"BigQuery insert errors: {errors}",
                    "exported": len(rows) - len(errors),
                    "failed": len(errors)
                }
            
            return {
                "success": True,
                "exported": len(rows),
                "failed": 0
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error batch exporting to BigQuery: {str(e)}"
            }


# Singleton instance
_bigquery_service_instance = None


def get_bigquery_service() -> BigQueryService:
    """Get or create BigQueryService singleton instance."""
    global _bigquery_service_instance
    if _bigquery_service_instance is None:
        _bigquery_service_instance = BigQueryService()
    return _bigquery_service_instance


