"""
SKILLS: bootstrap (unified)
PURPOSE: Auto-register all built-in skills (discovery, persona, outreach, qualification)
"""
import logging

from src.skills.skill_registry import register_skill, get_skill_names
from src.skills.discovery.company_discovery_skill import CompanyDiscoverySkill
from src.skills.discovery.company_analysis_skill import CompanyAnalysisSkill
from src.skills.discovery.company_filter_skill import CompanyFilterSkill
from src.skills.discovery.similar_company_finder_skill import SimilarCompanyFinderSkill
from src.skills.persona.decision_maker_detection_skill import DecisionMakerDetectionSkill
from src.skills.persona.decision_maker_selection_skill import DecisionMakerSelectionSkill
from src.skills.outreach.email_generation_skill import EmailGenerationSkill
from src.skills.outreach.followup_generation_skill import FollowupGenerationSkill
from src.skills.qualification.lead_scoring_skill import LeadScoringSkill
from src.skills.enrichment.contact_enrichment_skill import ContactEnrichmentSkill

logger = logging.getLogger(__name__)

_bootstrapped = False


def bootstrap_skills() -> None:
    """Register all skills (idempotent). Call on app startup or first use."""
    global _bootstrapped
    if _bootstrapped:
        return
    register_skill("company_discovery", CompanyDiscoverySkill)
    register_skill("company_analysis", CompanyAnalysisSkill)
    register_skill("company_filter", CompanyFilterSkill)
    register_skill("similar_company_finder", SimilarCompanyFinderSkill)
    register_skill("decision_maker_detection", DecisionMakerDetectionSkill)
    register_skill("decision_maker_selection", DecisionMakerSelectionSkill)
    register_skill("email_generation", EmailGenerationSkill)
    register_skill("followup_generation", FollowupGenerationSkill)
    register_skill("lead_scoring", LeadScoringSkill)
    register_skill("contact_enrichment", ContactEnrichmentSkill)
    _bootstrapped = True
    logger.info("skills: bootstrap complete %s", get_skill_names())


def list_skill_names() -> list:
    return get_skill_names()
