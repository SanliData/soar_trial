"""

ROUTER: agent_proxy_firewall_router

PURPOSE: HTTP facade for AI proxy firewall governance (H-039)

ENCODING: UTF-8 WITHOUT BOM

"""



from __future__ import annotations



from typing import Any, Dict



from fastapi import APIRouter



from src.agent_proxy_firewall.compression_resilience_service import export_compression_resilience_manifest

from src.agent_proxy_firewall.execution_firewall_service import export_execution_firewall_manifest

from src.agent_proxy_firewall.input_filter_chain_service import export_input_filter_chain_manifest

from src.agent_proxy_firewall.output_filter_chain_service import export_output_filter_chain_manifest

from src.agent_proxy_firewall.policy_interceptor_service import export_policy_interception_manifest

from src.agent_proxy_firewall.proxy_gateway_service import export_proxy_gateways_manifest

from src.agent_proxy_firewall.runtime_anomaly_alignment_service import export_runtime_anomaly_alignment_manifest

from src.agent_proxy_firewall.sensitive_action_guard_service import export_protected_actions_manifest

from src.agent_proxy_firewall.trace_interception_service import export_interception_traces



router = APIRouter(tags=["agent-proxy-firewall"])





def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:

    merged: Dict[str, Any] = {

        "agent_proxy_firewall_foundation": True,

        "unrestricted_autonomous_execution": False,

        "hidden_runtime_bypasses": False,

        "dynamic_self_modifying_policies": False,

        "direct_agent_provider_trust": False,

    }

    merged.update(payload)

    return merged





@router.get("/system/firewall/gateways")

async def list_firewall_gateways() -> Dict[str, Any]:

    return _envelope(

        {

            "gateways": export_proxy_gateways_manifest(),

            "compression_resilience": export_compression_resilience_manifest(),

            "runtime_inference_alignment": export_runtime_anomaly_alignment_manifest(),

        }

    )





@router.get("/system/firewall/input-filters")

async def list_input_filters() -> Dict[str, Any]:

    return _envelope({"input_filters": export_input_filter_chain_manifest()})





@router.get("/system/firewall/output-filters")

async def list_output_filters() -> Dict[str, Any]:

    return _envelope({"output_filters": export_output_filter_chain_manifest()})





@router.get("/system/firewall/policies")

async def list_firewall_policies() -> Dict[str, Any]:

    pole = export_policy_interception_manifest()

    exfw = export_execution_firewall_manifest()

    return _envelope({"policies": {**pole, "execution_firewall": exfw}})





@router.get("/system/firewall/protected-actions")

async def list_protected_actions() -> Dict[str, Any]:

    return _envelope({"protected_actions": export_protected_actions_manifest()})





@router.get("/system/firewall/interception-traces")

async def list_interception_traces() -> Dict[str, Any]:

    return _envelope({"interception_traces": export_interception_traces()})

