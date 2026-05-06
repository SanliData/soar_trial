from dataclasses import dataclass


@dataclass(frozen=True)
class MatchRequest:
    requester_id: str
    lat: float
    lng: float
    radius_meters: int


@dataclass(frozen=True)
class MatchResult:
    provider_id: str
    score: float
    distance_meters: int

    def __post_init__(self):
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("score must be between 0.0 and 1.0")
