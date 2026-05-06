"""
SERVICE: web_acquisition.service
PURPOSE: Main web acquisition service
ENCODING: UTF-8 WITHOUT BOM

Manages acquisition jobs, enforces caps, integrates with Stagehand adapter.
"""

import uuid
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from src.models.acquisition_job import AcquisitionJob, AcquisitionResult, EvidenceSource
from src.services.web_acquisition.interfaces import (
    AcquisitionJobRequest,
    AcquisitionJobResult,
    CoverageReport
)
from src.services.web_acquisition.stagehand_adapter import get_stagehand_adapter
from src.services.web_acquisition.compliance import SourcesPolicy
from src.core.query_limits import MAX_RESULTS_PER_QUERY, enforce_query_limit

logger = logging.getLogger(__name__)


class WebAcquisitionService:
    """
    Main web acquisition service.
    Manages jobs, enforces caps, integrates with Stagehand.
    """
    
    def __init__(self):
        """Initialize web acquisition service."""
        self.stagehand = get_stagehand_adapter()
    
    def create_job(
        self,
        request: AcquisitionJobRequest,
        db: Session,
        is_admin: bool = False
    ) -> AcquisitionJob:
        """
        Create a new acquisition job.
        
        Args:
            request: Acquisition job request
            db: Database session
            is_admin: Whether user is admin (for cap override)
            
        Returns:
            Created AcquisitionJob
        """
        ***REMOVED*** Enforce max_results cap
        max_results = enforce_query_limit(request.max_results, is_admin=is_admin)
        
        ***REMOVED*** Validate sources policy
        if not SourcesPolicy.validate_sources_policy(request.sources_policy):
            raise ValueError(f"Invalid sources_policy: {request.sources_policy}")
        
        ***REMOVED*** Generate unique job ID
        job_id = str(uuid.uuid4())
        
        ***REMOVED*** Create job
        job = AcquisitionJob(
            job_id=job_id,
            plan_id=request.plan_id,
            target_type=request.target_type,
            geography=str(request.geography) if request.geography else None,
            sources_policy=request.sources_policy,
            max_results=max_results,
            status="queued"
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        logger.info(f"Created acquisition job {job_id} for plan {request.plan_id}")
        
        return job
    
    async def execute_job(
        self,
        job_id: str,
        db: Session
    ) -> AcquisitionJob:
        """
        Execute an acquisition job (async worker).
        
        Args:
            job_id: Job ID
            db: Database session
            
        Returns:
            Updated AcquisitionJob
        """
        ***REMOVED*** Get job
        job = db.query(AcquisitionJob).filter(AcquisitionJob.job_id == job_id).first()
        if not job:
            raise ValueError(f"Job not found: {job_id}")
        
        if job.status not in ["queued", "running"]:
            raise ValueError(f"Job {job_id} is not in queued/running state")
        
        ***REMOVED*** Update status to running
        job.status = "running"
        job.started_at = datetime.utcnow()
        db.commit()
        
        try:
            ***REMOVED*** Parse geography if available
            geography = None
            if job.geography:
                import json
                try:
                    geography = json.loads(job.geography)
                except:
                    pass
            
            ***REMOVED*** Execute acquisition via Stagehand adapter
            result = await self.stagehand.acquire_data(
                target_type=job.target_type,
                geography=geography,
                sources_policy=job.sources_policy,
                max_results=job.max_results,
                plan_id=job.plan_id
            )
            
            ***REMOVED*** Store results in database
            self._store_results(job, result, db)
            
            ***REMOVED*** Update job status
            job.status = "ready"
            job.completed_at = datetime.utcnow()
            job.coverage_report = result.coverage_report.dict()
            db.commit()
            
            logger.info(f"Acquisition job {job_id} completed successfully")
            
        except Exception as e:
            ***REMOVED*** Mark job as failed
            job.status = "failed"
            job.error_message = str(e)
            job.error_details = {"exception_type": type(e).__name__}
            db.commit()
            
            logger.error(f"Acquisition job {job_id} failed: {e}", exc_info=True)
            raise
        
        return job
    
    def _store_results(
        self,
        job: AcquisitionJob,
        result: AcquisitionJobResult,
        db: Session
    ):
        """
        Store acquisition results in database.
        
        Args:
            job: AcquisitionJob
            result: AcquisitionJobResult
            db: Database session
        """
        ***REMOVED*** Store businesses
        for business in result.businesses:
            db_result = AcquisitionResult(
                job_id=job.id,
                result_type="business",
                business_name=business.name,
                business_address=business.address,
                business_website=business.website,
                business_phone=business.phone,
                business_industry=business.industry,
                business_metadata=business.metadata
            )
            db.add(db_result)
        
        ***REMOVED*** Store contacts
        for contact in result.contacts:
            db_result = AcquisitionResult(
                job_id=job.id,
                result_type="contact",
                contact_name=contact.name,
                contact_email=contact.email,
                contact_phone=contact.phone,
                contact_job_title=contact.job_title,
                contact_department=contact.department,
                contact_seniority=contact.seniority,
                contact_metadata=contact.metadata
            )
            db.add(db_result)
        
        ***REMOVED*** Store evidence sources
        for evidence in result.evidence:
            db_evidence = EvidenceSource(
                job_id=job.id,
                domain=evidence.domain,
                url=evidence.url,
                source_type=evidence.source_type,
                businesses_found=evidence.businesses_found,
                contacts_found=evidence.contacts_found
            )
            db.add(db_evidence)
        
        db.commit()
    
    def get_job(
        self,
        job_id: str,
        db: Session
    ) -> Optional[AcquisitionJob]:
        """
        Get acquisition job by ID.
        
        Args:
            job_id: Job ID
            db: Database session
            
        Returns:
            AcquisitionJob or None
        """
        return db.query(AcquisitionJob).filter(AcquisitionJob.job_id == job_id).first()
    
    def get_job_results(
        self,
        job: AcquisitionJob,
        db: Session
    ) -> AcquisitionJobResult:
        """
        Get results for an acquisition job.
        
        Args:
            job: AcquisitionJob
            db: Database session
            
        Returns:
            AcquisitionJobResult
        """
        from src.services.web_acquisition.interfaces import (
            BusinessAcquired,
            ContactAcquired,
            EvidenceSourceInfo
        )
        
        ***REMOVED*** Get results from database
        db_results = db.query(AcquisitionResult).filter(
            AcquisitionResult.job_id == job.id
        ).all()
        
        businesses: list = []
        contacts: list = []
        
        for db_result in db_results:
            if db_result.result_type == "business":
                businesses.append(BusinessAcquired(
                    name=db_result.business_name or "",
                    address=db_result.business_address,
                    website=db_result.business_website,
                    phone=db_result.business_phone,
                    industry=db_result.business_industry,
                    metadata=db_result.business_metadata
                ))
            elif db_result.result_type == "contact":
                contacts.append(ContactAcquired(
                    name=db_result.contact_name,
                    email=db_result.contact_email,
                    phone=db_result.contact_phone,
                    job_title=db_result.contact_job_title,
                    department=db_result.contact_department,
                    seniority=db_result.contact_seniority,
                    metadata=db_result.contact_metadata
                ))
        
        ***REMOVED*** Get evidence sources
        db_evidence = db.query(EvidenceSource).filter(
            EvidenceSource.job_id == job.id
        ).all()
        
        evidence = [
            EvidenceSourceInfo(
                domain=e.domain,
                url=e.url,
                source_type=e.source_type,
                businesses_found=e.businesses_found,
                contacts_found=e.contacts_found
            )
            for e in db_evidence
        ]
        
        ***REMOVED*** Build coverage report
        coverage_report = CoverageReport(
            businesses_found=len(businesses),
            contacts_found=len(contacts),
            emails=sum(1 for c in contacts if c.email),
            phones=sum(1 for c in contacts if c.phone) + sum(1 for b in businesses if b.phone),
            websites=sum(1 for b in businesses if b.website),
            is_capped=job.coverage_report.get("is_capped", False) if job.coverage_report else False,
            capped_at=job.coverage_report.get("capped_at") if job.coverage_report else None
        )
        
        return AcquisitionJobResult(
            businesses=businesses,
            contacts=contacts,
            evidence=evidence,
            coverage_report=coverage_report
        )


***REMOVED*** Global service instance
_acquisition_service: Optional[WebAcquisitionService] = None


def get_acquisition_service() -> WebAcquisitionService:
    """Get global web acquisition service instance."""
    global _acquisition_service
    if _acquisition_service is None:
        _acquisition_service = WebAcquisitionService()
    return _acquisition_service
