"""
SERVICE: result_service
PURPOSE: Result delivery and export management service
ENCODING: UTF-8 WITHOUT BOM
"""

import logging
import uuid
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session

from src.models.plan_result import PlanResult, ResultModule
from src.models.plan_lifecycle import PlanLifecycle
from src.models.export_job import ExportJob
from src.core.query_limits import MAX_RESULTS_PER_QUERY, should_show_capped_warning

logger = logging.getLogger(__name__)


class ResultService:
    """Service for managing plan results and exports"""
    
    def __init__(self, db: Session):
        self.db = db
        self.exports_dir = Path(__file__).parent.parent.parent.parent / "data" / "exports"
        self.exports_dir.mkdir(parents=True, exist_ok=True)
    
    def create_result_hub(self, plan_id: str) -> PlanResult:
        """Create Results Hub for a plan"""
        plan_result = PlanResult(
            plan_id=plan_id,
            status="pending"
        )
        self.db.add(plan_result)
        self.db.commit()
        self.db.refresh(plan_result)
        return plan_result
    
    def get_result_hub(self, plan_id: str) -> Optional[PlanResult]:
        """Get Results Hub for a plan"""
        return self.db.query(PlanResult).filter(PlanResult.plan_id == plan_id).first()
    
    def get_preview_report(self, plan_id: str) -> Dict[str, Any]:
        """
        Generate non-sensitive preview report (before purchase).
        Shows aggregated counts only, no PII.
        MAX 100 businesses shown (capped).
        """
        plan = self.db.query(PlanLifecycle).filter(PlanLifecycle.plan_id == plan_id).first()
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")
        
        ***REMOVED*** TODO: Calculate actual counts from data
        ***REMOVED*** For now, mock but enforce limits
        estimated_businesses = 1284  ***REMOVED*** Mock - replace with actual query count
        estimated_personas = 500  ***REMOVED*** Mock
        
        ***REMOVED*** Check if region is too large (warning trigger)
        region = plan.onboarding_data.get("geography", "N/A")
        is_large_region = should_show_capped_warning(estimated_businesses, MAX_RESULTS_PER_QUERY)
        
        preview = {
            "plan_id": plan_id,
            "target_region": region,
            "businesses_found": estimated_businesses,
            "businesses_available_sample": min(estimated_businesses, MAX_RESULTS_PER_QUERY),  ***REMOVED*** Capped to 100
            "relevant_departments": 3,  ***REMOVED*** Mock
            "target_personas": estimated_personas,
            "personas_available_sample": min(estimated_personas, MAX_RESULTS_PER_QUERY),  ***REMOVED*** Capped to 100
            "reachability": {
                "corporate_emails": 48,
                "linkedin_profiles": 77,
                "phones": 29,
                "location_targetable_audience": True
            },
            "status": "preview",
            "requires_refinement": is_large_region,  ***REMOVED*** True if region > 100 businesses
            "warning_message": f"This region contains more than {MAX_RESULTS_PER_QUERY} eligible businesses. Please refine your criteria or continue with a capped sample." if is_large_region else None,
            "note": "This is a preview. Full results will be available after confirmation. Maximum 100 results per query."
        }
        
        return preview
    
    def get_results(self, plan_id: str) -> Dict[str, Any]:
        """Get all results for a plan (Results Hub)"""
        plan_result = self.get_result_hub(plan_id)
        if not plan_result:
            ***REMOVED*** Return empty state instead of raising error - Results Hub not created yet
            return {
                "plan_id": plan_id,
                "status": "pending",
                "summary": None,
                "modules": [],
                "created_at": None,
                "updated_at": None,
                "completed_at": None
            }
        
        modules_data = [
            {
                "module_type": module.module_type,
                "status": module.status,
                "preview_data": module.preview_data,
                "ready_at": module.ready_at.isoformat() if module.ready_at else None
            }
            for module in plan_result.modules
        ]
        
        return {
            "plan_id": plan_id,
            "status": plan_result.status,
            "summary": plan_result.summary,
            "modules": modules_data,
            "created_at": plan_result.created_at.isoformat(),
            "updated_at": plan_result.updated_at.isoformat(),
            "completed_at": plan_result.completed_at.isoformat() if plan_result.completed_at else None
        }
    
    def create_export_job(
        self,
        plan_id: str,
        format: str,
        modules: Optional[List[str]] = None
    ) -> ExportJob:
        """Create async export job"""
        plan_result = self.get_result_hub(plan_id)
        if not plan_result:
            ***REMOVED*** Auto-create Results Hub if it doesn't exist
            plan_result = self.create_result_hub(plan_id)
        
        export_id = str(uuid.uuid4())
        
        export_job = ExportJob(
            export_id=export_id,
            plan_result_id=plan_result.id,
            format=format,
            modules=json.dumps(modules) if modules else None,
            status="pending"
        )
        self.db.add(export_job)
        self.db.commit()
        self.db.refresh(export_job)
        
        ***REMOVED*** TODO: Queue async export generation
        ***REMOVED*** For now, mark as processing
        export_job.status = "processing"
        self.db.commit()
        
        return export_job
    
    def get_export_status(self, export_id: str) -> Optional[ExportJob]:
        """Get export job status"""
        return self.db.query(ExportJob).filter(ExportJob.export_id == export_id).first()
    
    def get_export_file_path(self, export_id: str) -> Optional[Path]:
        """Get export file path if ready"""
        export_job = self.get_export_status(export_id)
        if not export_job or export_job.status != "ready":
            return None
        
        if export_job.file_path:
            return Path(export_job.file_path)
        return None

    def get_export_rows(self, plan_id: str) -> List[Dict[str, Any]]:
        """
        Collect cached result rows for export.
        Uses stored result modules to avoid re-running expensive queries.
        """
        plan_result = self.get_result_hub(plan_id)
        if not plan_result:
            raise ValueError(f"Results Hub for plan {plan_id} not found")
        
        rows: List[Dict[str, Any]] = []
        for module in plan_result.modules:
            rows.extend(self._extract_rows_from_module(module))
        
        if not rows:
            raise ValueError("No cached results available for export")
        
        ***REMOVED*** Deduplicate rows by company/address/role combo to avoid duplicate exports
        deduped_rows: List[Dict[str, Any]] = []
        seen_keys = set()
        for row in rows:
            key = (
                row.get("company_name"),
                row.get("address"),
                row.get("persona_role")
            )
            if key not in seen_keys:
                seen_keys.add(key)
                deduped_rows.append(row)
        
        return deduped_rows

    def _extract_rows_from_module(self, module: ResultModule) -> List[Dict[str, Any]]:
        """Extract normalized rows from a single result module."""
        if not module.result_data:
            return []
        
        data = module.result_data
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                logger.debug("Skipping module %s due to invalid JSON payload", module.module_type)
                return []
        
        records: List[Dict[str, Any]] = []
        if isinstance(data, list):
            records = [item for item in data if isinstance(item, dict)]
        elif isinstance(data, dict):
            candidate_lists = [
                data.get("records"),
                data.get("results"),
                data.get("businesses"),
                data.get("companies"),
                data.get("entries"),
                data.get("items"),
                data.get("data"),
            ]
            for candidate in candidate_lists:
                if isinstance(candidate, list):
                    records = [item for item in candidate if isinstance(item, dict)]
                    break
            else:
                ***REMOVED*** Treat dict itself as single record
                records = [data]
        else:
            return []
        
        normalized_rows = []
        for record in records:
            normalized = self._normalize_record(record)
            if normalized:
                normalized_rows.append(normalized)
        return normalized_rows

    @staticmethod
    def _normalize_record(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize heterogeneous record payloads into export-ready rows."""
        if not isinstance(record, dict):
            return None
        
        location_data = record.get("location") or record.get("address_info") or {}
        if isinstance(location_data, str):
            location_data = {"address": location_data}
        elif not isinstance(location_data, dict):
            location_data = {}
        
        def pick_value(source: Dict[str, Any], keys: List[str]) -> Optional[str]:
            for key in keys:
                value = source.get(key)
                if value is None:
                    continue
                if isinstance(value, (list, tuple)):
                    joined = ", ".join(str(item) for item in value if item)
                    if joined:
                        return joined
                elif isinstance(value, dict):
                    ***REMOVED*** try common nested keys
                    for nested_key in ("value", "name", "label", "text"):
                        nested_val = value.get(nested_key)
                        if nested_val:
                            return str(nested_val)
                else:
                    text = str(value).strip()
                    if text:
                        return text
            return None
        
        company_name = pick_value(record, ["company_name", "name", "business_name", "company", "title"])
        address = pick_value(
            record,
            ["address", "full_address", "street", "formatted_address", "address_line", "address_text"]
        ) or pick_value(location_data, ["address", "formatted_address", "line1"])
        city = pick_value(record, ["city", "locality"]) or pick_value(location_data, ["city", "locality"])
        postal_code = pick_value(
            record,
            ["zip", "postal_code", "zip_code", "postcode"]
        ) or pick_value(location_data, ["zip", "postal_code", "zip_code", "postcode"])
        persona_role = pick_value(
            record,
            ["persona_role", "role", "persona", "persona_name", "job_title", "decision_role"]
        )
        if not persona_role:
            roles = record.get("roles")
            if isinstance(roles, list):
                persona_role = ", ".join(str(role) for role in roles if role) or None
        
        contact_availability = pick_value(record, ["contact_availability", "contact_status"])
        if not contact_availability:
            contact_signals = [
                record.get("contacts"),
                record.get("contact_channels"),
                record.get("contact_details"),
                record.get("emails"),
                record.get("phones"),
                record.get("email"),
                record.get("phone"),
            ]
            has_contact = False
            for signal in contact_signals:
                if not signal:
                    continue
                if isinstance(signal, (list, tuple, set)):
                    has_contact = len([item for item in signal if item]) > 0
                else:
                    has_contact = True
                if has_contact:
                    break
            contact_availability = "Available" if has_contact else "Not available"
        else:
            contact_availability = contact_availability or "Not available"
        
        latitude = record.get("latitude") or record.get("lat") or location_data.get("latitude") or location_data.get("lat")
        longitude = record.get("longitude") or record.get("lng") or location_data.get("longitude") or location_data.get("lng")
        if latitude is not None and not isinstance(latitude, (int, float)):
            try:
                latitude = float(latitude)
            except (TypeError, ValueError):
                latitude = None
        if longitude is not None and not isinstance(longitude, (int, float)):
            try:
                longitude = float(longitude)
            except (TypeError, ValueError):
                longitude = None

        company_domain = pick_value(
            record,
            ["company_domain", "domain", "website", "website_url", "url", "company_website"]
        )
        company_size = pick_value(
            record,
            ["company_size", "employee_count", "employees", "size", "headcount"]
        )
        industry = pick_value(
            record,
            ["industry", "sector", "vertical", "naics", "sic"]
        )
        country = pick_value(
            record,
            ["country", "country_code", "nation"]
        ) or pick_value(location_data, ["country", "country_code"])
        keyword_intent = pick_value(
            record,
            ["keyword", "service_intent", "keywords", "services", "products", "verified_services", "product_service"]
        )
        if not keyword_intent and isinstance(record.get("services"), list):
            keyword_intent = ", ".join(str(s) for s in record["services"] if s)[:500] or None
        if not keyword_intent and isinstance(record.get("products"), list):
            keyword_intent = ", ".join(str(p) for p in record["products"] if p)[:500] or None

        normalized_record = {
            "company_name": company_name or "N/A",
            "address": address or "N/A",
            "city": city or "N/A",
            "zip": postal_code or "N/A",
            "persona_role": persona_role or "N/A",
            "contact_availability": contact_availability or "Not available",
            "latitude": latitude,
            "longitude": longitude,
            "company_domain": (company_domain or "").strip() or "",
            "company_size": (company_size or "").strip() or "",
            "industry": (industry or "").strip() or "",
            "country": (country or "").strip() or "",
            "keyword_intent": (keyword_intent or "").strip() or "",
        }
        return normalized_record


def get_result_service(db: Session) -> ResultService:
    """Get result service instance"""
    return ResultService(db)
