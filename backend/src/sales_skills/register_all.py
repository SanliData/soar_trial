"""
SALES_SKILLS: register_all
PURPOSE: Register all sales skills with the registry (call on import or startup)
"""
from src.sales_skills.skill_registry import register_skill
from src.sales_skills.discovery.company_discovery_skill import CompanyDiscoverySkill
from src.sales_skills.discovery.similar_company_finder import SimilarCompanyFinderSkill
from src.sales_skills.persona.decision_maker_selection_skill import DecisionMakerSelectionSkill
from src.sales_skills.outreach.email_generation_skill import EmailGenerationSkill
from src.sales_skills.outreach.followup_generation_skill import FollowupGenerationSkill
from src.sales_skills.qualification.lead_scoring_skill import LeadScoringSkill


def register_all_sales_skills() -> None:
    register_skill("company_discovery", CompanyDiscoverySkill)
    register_skill("similar_company_finder", SimilarCompanyFinderSkill)
    register_skill("decision_maker_selection", DecisionMakerSelectionSkill)
    register_skill("email_generation", EmailGenerationSkill)
    register_skill("followup_generation", FollowupGenerationSkill)
    register_skill("lead_scoring", LeadScoringSkill)
