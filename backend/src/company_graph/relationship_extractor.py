import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def extract_company_relationships(db_session: Any) -> Dict[str, List]:
    nodes, edges = [], []
    try:
        from src.models.intel_company import IntelCompany
        from src.models.intel_contact import IntelContact
        from src.models.intel_campaign import IntelCampaign
        ind_set, geo_set = set(), set()
        for c in db_session.query(IntelCompany).limit(10000).all():
            nodes.append({"id": "company_%s" % c.id, "type": "company", "label": c.company_name, "properties": {"industry": c.industry, "location": c.location}})
            if c.industry and c.industry not in ind_set:
                ind_set.add(c.industry)
                nid = "industry_%s" % (c.industry or "").replace(" ", "_")[:64]
                nodes.append({"id": nid, "type": "industry", "label": c.industry, "properties": {}})
                edges.append({"type": "company_belongs_to_industry", "source_id": "company_%s" % c.id, "target_id": nid, "properties": {}})
            if c.location and c.location not in geo_set:
                geo_set.add(c.location)
                gid = "geography_%s" % (c.location or "").replace(" ", "_")[:64]
                nodes.append({"id": gid, "type": "geography", "label": c.location, "properties": {}})
        for r in db_session.query(IntelContact).limit(10000).all():
            nodes.append({"id": "contact_%s" % r.id, "type": "contact", "label": r.name, "properties": {"role": r.role}})
            edges.append({"type": "company_has_contact", "source_id": "company_%s" % r.company_id, "target_id": "contact_%s" % r.id, "properties": {}})
        for camp in db_session.query(IntelCampaign).limit(5000).all():
            nodes.append({"id": "campaign_%s" % camp.id, "type": "campaign", "label": camp.campaign_id or "", "properties": {}})
    except Exception as e:
        logger.exception("extract_company_relationships: %s", e)
    return {"nodes": nodes, "edges": edges}
