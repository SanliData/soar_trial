***REMOVED*** -*- coding: utf-8 -*-
"""
Customer Pool Service - Customer pool creation
Creates target customer pool with information such as official address, website
"""

from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.b2b_company import Company
from backend.db import SessionLocal


class CustomerPoolService:
    """Customer pool creation and management service"""
    
    def _get_db(self) -> Session:
        """Get database session"""
        db = SessionLocal()
        try:
            return db
        finally:
            pass  ***REMOVED*** Calling code will close the session
    
    def create_company(
        self,
        name: str,
        official_name: Optional[str] = None,
        website: Optional[str] = None,
        industry: Optional[str] = None,
        company_size: Optional[str] = None,
        address_line1: Optional[str] = None,
        address_line2: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        postal_code: Optional[str] = None,
        country: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Company:
        """Create new company record"""
        db = self._get_db()
        try:
            company = Company(
                name=name,
                official_name=official_name or name,
                website=website,
                industry=industry,
                company_size=company_size,
                address_line1=address_line1,
                address_line2=address_line2,
                city=city,
                state=state,
                postal_code=postal_code,
                country=country,
                metadata=metadata or {},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(company)
            db.commit()
            db.refresh(company)
            
            return company
        finally:
            db.close()
    
    def bulk_create_companies(self, companies_data: List[Dict]) -> List[Company]:
        """Bulk create company records"""
        db = self._get_db()
        try:
            companies = []
            
            for data in companies_data:
                company = Company(
                    name=data.get("name", ""),
                    official_name=data.get("official_name") or data.get("name", ""),
                    website=data.get("website"),
                    industry=data.get("industry"),
                    company_size=data.get("company_size"),
                    address_line1=data.get("address_line1"),
                    address_line2=data.get("address_line2"),
                    city=data.get("city"),
                    state=data.get("state"),
                    postal_code=data.get("postal_code"),
                    country=data.get("country"),
                    metadata=data.get("metadata", {}),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                companies.append(company)
                db.add(company)
            
            db.commit()
            for company in companies:
                db.refresh(company)
            
            return companies
        finally:
            db.close()
    
    def search_companies(
        self,
        name: Optional[str] = None,
        industry: Optional[str] = None,
        city: Optional[str] = None,
        country: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Company]:
        """Search companies"""
        db = self._get_db()
        try:
            query = db.query(Company)
            
            if name:
                query = query.filter(Company.name.ilike(f"%{name}%"))
            if industry:
                query = query.filter(Company.industry.ilike(f"%{industry}%"))
            if city:
                query = query.filter(Company.city.ilike(f"%{city}%"))
            if country:
                query = query.filter(Company.country.ilike(f"%{country}%"))
            
            return query.offset(offset).limit(limit).all()
        finally:
            db.close()
    
    def get_company_by_id(self, company_id: int) -> Optional[Company]:
        """Get company by ID"""
        db = self._get_db()
        try:
            return db.query(Company).filter(Company.id == company_id).first()
        finally:
            db.close()
    
    def update_company(self, company_id: int, **kwargs) -> Optional[Company]:
        """Update company information"""
        db = self._get_db()
        try:
            company = db.query(Company).filter(Company.id == company_id).first()
            
            if not company:
                return None
            
            for key, value in kwargs.items():
                if hasattr(company, key) and value is not None:
                    setattr(company, key, value)
            
            company.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(company)
            
            return company
        finally:
            db.close()
    
    def get_companies_without_address_validation(self, limit: int = 100) -> List[Company]:
        """Get companies without address validation"""
        db = self._get_db()
        try:
            return db.query(Company).filter(
                Company.address_validated == False
            ).limit(limit).all()
        finally:
            db.close()
    
    def get_companies_without_coordinates(self, limit: int = 100) -> List[Company]:
        """Get companies without coordinates"""
        db = self._get_db()
        try:
            return db.query(Company).filter(
                (Company.latitude == None) | (Company.longitude == None)
            ).limit(limit).all()
        finally:
            db.close()
    
    def get_pool_statistics(self) -> Dict:
        """Get customer pool statistics"""
        db = self._get_db()
        try:
            total = db.query(Company).count()
            validated = db.query(Company).filter(Company.address_validated == True).count()
            with_coordinates = db.query(Company).filter(
                (Company.latitude != None) & (Company.longitude != None)
            ).count()
            with_website = db.query(Company).filter(Company.website != None).count()
            
            return {
                "total_companies": total,
                "address_validated": validated,
                "with_coordinates": with_coordinates,
                "with_website": with_website,
                "validation_rate": (validated / total * 100) if total > 0 else 0,
            }
        finally:
            db.close()


***REMOVED*** Global instance
customer_pool_service = CustomerPoolService()

