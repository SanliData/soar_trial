***REMOVED*** H-029 — Agent Security, Isolation & Trust Boundary Layer

**Scope:** Security foundation — deterministic policies, static capability registry, sanitizers, audit traces. **No** autonomous tool execution or MCP runtime.

***REMOVED******REMOVED*** Threat model (abbreviated)

| Risk | Mitigation in this layer |
|------|---------------------------|
| Prompt injection / instruction hijack | Regex + delimiter heuristics; zero-width stripping; tagged findings |
| Tool poisoning / capability escalation | Static `TOOL_REGISTRY`; fail-closed validation; no runtime mutation |
| Retrieval poisoning | Script stripping; CSS-hidden indicators; tool-directive tokens; bidi stripping |
| Cross-tool hijacking | Explicit `ALLOWED_DELEGATIONS` pairs only |
| Ambient trust creep | `assert_escalation_blocked` across trust tiers |

***REMOVED******REMOVED*** Trust levels (registry)

- `verified_internal`
- `trusted_partner`
- `external_unverified`
- `sandbox_only`

Each tool record includes: allowed actions, domains, external execution flag, human-approval requirements, risk tier.

***REMOVED******REMOVED*** HTTP surface

| Method | Path |
|--------|------|
| GET | `/api/v1/system/security/capabilities` |
| POST | `/api/v1/system/security/sanitize-prompt` |
| POST | `/api/v1/system/security/sanitize-retrieval` |
| GET | `/api/v1/system/security/traces` |
| POST | `/api/v1/system/security/risk-score` |

Responses include governance flags: `agent_security_foundation`, `autonomous_tool_execution=false`, `unrestricted_mcp_execution=false`.

***REMOVED******REMOVED*** Semantic capabilities (H-020)

- `security.list_capabilities` (read)
- `security.sanitize_prompt`
- `security.sanitize_retrieval`
- `security.risk_score` — **human_approval_required=true** (orchestration must not auto-act on score alone)

***REMOVED******REMOVED*** Explicit deferrals

- Unrestricted MCP integration and execution
- Dynamic capability expansion at runtime
- Autonomous multi-agent delegation graphs
- Arbitrary code execution (`eval`, shell, subprocess) from agent paths

***REMOVED******REMOVED*** Verification

```bash
python scripts/verify_h029_agent_security.py
cd backend && python -m pytest tests/test_agent_security.py -q
```
