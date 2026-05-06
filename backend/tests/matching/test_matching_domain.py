from src.matching.domain import MatchRequest, MatchResult


def test_match_request_creation():
    req = MatchRequest(
        requester_id="user-1",
        lat=40.0,
        lng=29.0,
        radius_meters=500
    )
    assert req.requester_id == "user-1"
    assert req.radius_meters == 500


def test_match_result_score_range():
    result = MatchResult(
        provider_id="tech-1",
        score=0.85,
        distance_meters=120
    )
    assert 0.0 <= result.score <= 1.0
