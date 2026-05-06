"""
PACKAGE: mcp_runtime
PURPOSE: MCP runtime compatibility layer (projection only) (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from src.mcp_runtime.mcp_agent_gateway import export_mcp_gateway_manifest   # noqa: F401
from src.mcp_runtime.mcp_capability_registry import export_mcp_capability_registry   # noqa: F401
from src.mcp_runtime.mcp_tool_projection_service import project_mcp_tools   # noqa: F401
from src.mcp_runtime.mcp_transport_service import export_mcp_transport_manifest   # noqa: F401
from src.mcp_runtime.mcp_runtime_validation import validate_mcp_tool_projection   # noqa: F401

