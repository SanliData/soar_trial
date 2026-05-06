from __future__ import annotations


def test_opportunity_scoring_deterministic():
    from src.results_hub.opportunity_card_service import export_opportunities

    a = export_opportunities()
    b = export_opportunities()
    assert a == b
    assert a["opportunities"]
    assert 0.0 <= a["opportunities"][0]["relevance_score"] <= 1.0
    assert a["opportunities"][0]["retrieval_sources"][0]["source_name"]


def test_explainability_deterministic_and_no_hidden_scoring():
    from src.results_hub.explainability_panel_service import export_explainability_panels

    a = export_explainability_panels()
    b = export_explainability_panels()
    assert a == b
    assert a["hidden_ranking_logic"] is False
    assert a["explainability"][0]["scoring_explanation"]["hidden_ranking_logic"] is False


def test_recommendations_are_not_autonomous():
    from src.results_hub.workflow_recommendation_service import export_recommendations

    out = export_recommendations()
    assert out["autonomous_action_execution"] is False
    assert out["recommendations_only"] is True

