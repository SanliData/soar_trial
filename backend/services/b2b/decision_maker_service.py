***REMOVED*** -*- coding: utf-8 -*-
"""
Decision Maker Service - Decision maker identification service
Identifies decision maker roles such as purchasing, R&D, owner
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from backend.models.b2b_persona import Persona
from backend.db import SessionLocal


class DecisionMakerService:
    """Decision maker identification and categorization service"""
    
    ***REMOVED*** Decision maker keywords (Turkish and English)
    DECISION_MAKER_KEYWORDS = {
        "purchasing": {
            "titles": [
                "satın alma", "purchasing", "procurement", "buyer", "sourcing",
                "satın alma müdürü", "purchasing manager", "procurement manager",
                "satın alma uzmanı", "purchasing specialist", "buyer specialist"
            ],
            "departments": ["satın alma", "purchasing", "procurement", "sourcing"]
        },
        "rnd": {
            "titles": [
                "ar-ge", "r&d", "research", "development", "innovation",
                "ar-ge müdürü", "r&d manager", "research director",
                "ar-ge uzmanı", "r&d specialist", "innovation manager",
                "teknoloji", "technology", "cto", "chief technology officer"
            ],
            "departments": ["ar-ge", "r&d", "research", "development", "innovation", "technology"]
        },
        "owner": {
            "titles": [
                "owner", "sahip", "kurucu", "founder", "ceo", "chief executive",
                "genel müdür", "general manager", "managing director",
                "yönetim kurulu", "board", "chairman", "başkan"
            ],
            "departments": ["yönetim", "management", "executive"]
        },
        "finance": {
            "titles": [
                "finans", "finance", "cfo", "chief financial officer",
                "finans müdürü", "finance manager", "financial director",
                "muhasebe", "accounting", "controller"
            ],
            "departments": ["finans", "finance", "accounting", "muhasebe"]
        },
        "operations": {
            "titles": [
                "operasyon", "operations", "coo", "chief operating officer",
                "operasyon müdürü", "operations manager", "operational director",
                "üretim", "production", "manufacturing"
            ],
            "departments": ["operasyon", "operations", "production", "üretim"]
        },
        "sales": {
            "titles": [
                "satış", "sales", "cso", "chief sales officer",
                "satış müdürü", "sales manager", "sales director",
                "business development", "iş geliştirme"
            ],
            "departments": ["satış", "sales", "business development", "iş geliştirme"]
        }
    }
    
    ***REMOVED*** Seniority levels
    SENIORITY_KEYWORDS = {
        "c_level": ["ceo", "cto", "cfo", "coo", "cso", "chief", "genel müdür", "başkan"],
        "director": ["director", "direktör", "müdür", "manager"],
        "senior": ["senior", "kıdemli", "lead", "lider"],
        "manager": ["manager", "müdür", "supervisor", "süpervizör"]
    }
    
    def _get_db(self) -> Session:
        """Get database session"""
        return SessionLocal()
    
    def identify_decision_maker_type(
        self,
        job_title: Optional[str] = None,
        department: Optional[str] = None
    ) -> Optional[str]:
        """Identify decision maker type from job title and department information"""
        if not job_title and not department:
            return None
        
        job_title_lower = (job_title or "").lower()
        department_lower = (department or "").lower()
        
        ***REMOVED*** Check for each decision maker type
        for dm_type, keywords in self.DECISION_MAKER_KEYWORDS.items():
            ***REMOVED*** Title check
            for title_keyword in keywords["titles"]:
                if title_keyword.lower() in job_title_lower:
                    return dm_type
            
            ***REMOVED*** Department check
            for dept_keyword in keywords["departments"]:
                if dept_keyword.lower() in department_lower:
                    return dm_type
        
        return None
    
    def identify_seniority_level(self, job_title: Optional[str] = None) -> Optional[str]:
        """Identify seniority level from job title"""
        if not job_title:
            return None
        
        job_title_lower = job_title.lower()
        
        ***REMOVED*** Check from high to low
        for level, keywords in self.SENIORITY_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in job_title_lower:
                    return level
        
        return "other"
    
    def calculate_decision_authority(
        self,
        decision_maker_type: Optional[str],
        seniority_level: Optional[str]
    ) -> str:
        """Calculate decision authority level"""
        if not decision_maker_type:
            return "low"
        
        ***REMOVED*** C-Level and Owner have high authority
        if seniority_level == "c_level" or decision_maker_type == "owner":
            return "high"
        
        ***REMOVED*** Director level is medium-high
        if seniority_level == "director":
            return "medium"
        
        ***REMOVED*** Manager level is medium
        if seniority_level == "manager":
            return "medium"
        
        ***REMOVED*** Other cases
        return "low"
    
    def classify_persona(
        self,
        job_title: Optional[str] = None,
        department: Optional[str] = None
    ) -> Dict:
        """Classify persona and return decision maker information"""
        decision_maker_type = self.identify_decision_maker_type(job_title, department)
        seniority_level = self.identify_seniority_level(job_title)
        decision_authority = self.calculate_decision_authority(decision_maker_type, seniority_level)
        
        is_decision_maker = decision_maker_type is not None
        
        return {
            "is_decision_maker": is_decision_maker,
            "decision_maker_type": decision_maker_type,
            "seniority_level": seniority_level,
            "decision_authority": decision_authority
        }
    
    def update_persona_decision_maker_info(self, persona: Persona) -> Persona:
        """Update persona's decision maker information"""
        classification = self.classify_persona(
            job_title=persona.job_title,
            department=persona.department
        )
        
        db = self._get_db()
        try:
            persona.is_decision_maker = classification["is_decision_maker"]
            persona.decision_maker_type = classification["decision_maker_type"]
            persona.seniority_level = classification["seniority_level"]
            persona.decision_authority = classification["decision_authority"]
            
            db.commit()
            db.refresh(persona)
            
            return persona
        finally:
            db.close()
    
    def find_decision_makers_by_type(
        self,
        company_id: Optional[int] = None,
        decision_maker_type: Optional[str] = None,
        min_authority: str = "low"  ***REMOVED*** low, medium, high
    ) -> List[Persona]:
        """Find decision makers of specific type"""
        db = self._get_db()
        try:
            query = db.query(Persona).filter(Persona.is_decision_maker == True)
            
            if company_id:
                query = query.filter(Persona.company_id == company_id)
            
            if decision_maker_type:
                query = query.filter(Persona.decision_maker_type == decision_maker_type)
            
            ***REMOVED*** Authority filtering
            authority_order = {"low": 1, "medium": 2, "high": 3}
            min_level = authority_order.get(min_authority, 1)
            
            personas = query.all()
            
            ***REMOVED*** Filter by authority
            filtered = []
            for persona in personas:
                persona_level = authority_order.get(persona.decision_authority or "low", 1)
                if persona_level >= min_level:
                    filtered.append(persona)
            
            return filtered
        finally:
            db.close()
    
    def get_decision_maker_statistics(self, company_id: Optional[int] = None) -> Dict:
        """Get decision maker statistics"""
        db = self._get_db()
        try:
            query = db.query(Persona).filter(Persona.is_decision_maker == True)
            
            if company_id:
                query = query.filter(Persona.company_id == company_id)
            
            all_dms = query.all()
            
            stats = {
                "total_decision_makers": len(all_dms),
                "by_type": {},
                "by_authority": {"high": 0, "medium": 0, "low": 0},
                "by_seniority": {}
            }
            
            for dm in all_dms:
                ***REMOVED*** By type
                dm_type = dm.decision_maker_type or "unknown"
                stats["by_type"][dm_type] = stats["by_type"].get(dm_type, 0) + 1
                
                ***REMOVED*** By authority
                authority = dm.decision_authority or "low"
                stats["by_authority"][authority] = stats["by_authority"].get(authority, 0) + 1
                
                ***REMOVED*** By seniority
                seniority = dm.seniority_level or "unknown"
                stats["by_seniority"][seniority] = stats["by_seniority"].get(seniority, 0) + 1
            
            return stats
        finally:
            db.close()


***REMOVED*** Global instance
decision_maker_service = DecisionMakerService()

