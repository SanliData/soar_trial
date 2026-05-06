"""
TOOLS: email_tool
PURPOSE: MCP-ready email operations — run(input) -> dict; simulates send/template
"""
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def run(input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Email action: generate, send, or template. MCP-ready interface.
    action: "generate" | "send" | "template"
    Later can delegate to real MCP email server.
    """
    action = input.get("action", "generate")
    if action == "send":
        to = input.get("to", "")
        subject = input.get("subject", "")
        body = input.get("body", "")
        logger.info("email_tool: send to=%s subject=%s", to, subject[:50])
        return {"sent": True, "to": to, "message_id": "mock_msg_001"}
    if action == "template":
        template_id = input.get("template_id", "")
        variables = input.get("variables", {})
        return {"rendered_subject": variables.get("subject", "Re: Introduction"), "rendered_body": variables.get("body", "")}
    ***REMOVED*** generate: placeholder
    return {"subject": input.get("subject", "Re: Introduction"), "body": input.get("body", "")}
