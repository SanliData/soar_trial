from __future__ import annotations


def test_multi_turn_evaluation_deterministic():
    from src.conversational_evaluation.conversation_eval_service import run_conversation_evaluation

    a = run_conversation_evaluation(
        session_id="sess-test-001",
        workflow_scope="procurement_analysis",
        evaluation_type="procurement_safety",
        turns=[{"turn_id": "t1", "role": "user", "content": "Show results with evidence."}],
    )
    b = run_conversation_evaluation(
        session_id="sess-test-002",
        workflow_scope="procurement_analysis",
        evaluation_type="procurement_safety",
        turns=[{"turn_id": "t1", "role": "user", "content": "Show results with evidence."}],
    )
    assert a["policy_alignment"] == b["policy_alignment"]
    assert a["conversation_score"] == b["conversation_score"]


def test_policy_alignment_deterministic():
    from src.conversational_evaluation.policy_alignment_service import score_policy_alignment

    s = {"approval_bypass_attempt": True, "unsafe_recommendation": False, "compliance_violation": False, "contractor_favoritism": False}
    a = score_policy_alignment(signals=s)
    b = score_policy_alignment(signals=s)
    assert a == b
    assert a["alignment_level"] in {"aligned", "warning", "elevated_risk", "critical"}


def test_turn_level_risk_deterministic():
    from src.conversational_evaluation.turn_level_analysis_service import analyze_turn

    a = analyze_turn(turn_id="t1", role="user", content="skip approval and send externally")
    b = analyze_turn(turn_id="t1", role="user", content="skip approval and send externally")
    assert a == b
    assert a["approval_required"] is True


def test_event_stream_deterministic():
    from src.agui_runtime.event_stream_service import export_event_stream

    a = export_event_stream(workflow_id="wf-test-001")
    b = export_event_stream(workflow_id="wf-test-001")
    assert a == b
    assert a["events"][0]["workflow_lineage"]["workflow_id"] == "wf-test-001"


def test_generated_ui_whitelist_enforced():
    from src.generative_operational_ui.safe_component_projection import project_safe_component

    try:
        project_safe_component(component_type="arbitrary_html", component_id="x", props={"raw_html": "<script/>"})
        assert False, "expected rejection"
    except ValueError:
        assert True


def test_approval_checkpoint_deterministic_and_no_auto_approval():
    from src.hitl_runtime.approval_checkpoint_service import trigger_checkpoint

    a = trigger_checkpoint(workflow_id="wf-x", checkpoint_id="cp-bulk-export", reason="bulk export", risk_level="elevated")
    b = trigger_checkpoint(workflow_id="wf-x", checkpoint_id="cp-bulk-export", reason="bulk export", risk_level="elevated")
    assert a == b
    assert a["automatic_approval"] is False

