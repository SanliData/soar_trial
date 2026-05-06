import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


async def route_response(reply_id: str, body: str, subject: str = "") -> Dict[str, Any]:
    """Route incoming response to analysis/classification agent."""
    try:
        from src.skills.sales.reply_classification_skill import ReplyClassificationSkill
        skill = ReplyClassificationSkill()
        ctx = await skill.run({"reply_body": body, "reply_subject": subject})
        logger.info("route_response: %s -> %s", reply_id, ctx.get("classification"))
        return {"ok": True, "reply_id": reply_id, "classification": ctx.get("classification"), "suggested_action": ctx.get("suggested_action")}
    except Exception as e:
        logger.exception("route_response: %s", e)
        return {"ok": False, "reply_id": reply_id, "error": str(e)}
