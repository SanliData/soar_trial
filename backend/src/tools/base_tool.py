"""
TOOLS: base_tool
PURPOSE: Base for MCP-ready tools — run(input: dict) -> dict
"""
from typing import Any, Dict


class BaseTool:
    """Base for tools that can be connected to MCP servers later."""

    name: str = "base_tool"
    description: str = ""

    def run(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool; input and output are dicts for MCP compatibility."""
        raise NotImplementedError
