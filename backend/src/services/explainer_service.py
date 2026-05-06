"""
SERVICE: explainer_service
PURPOSE: Service for generating "Why this account?" explanations
ENCODING: UTF-8 WITHOUT BOM

Generates explainability traces that show:
- Signals used
- Weights applied
- Exclusions applied
- Location affinity
- Confidence levels
"""

from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from src.models.target_trace import TargetTrace
from src.models.persona import Persona
from src.models.company import Company
from src.services.persona_signal_service import PersonaSignalService
from src.services.location_affinity_service import LocationAffinityService


class ExplainerService:
    """Service for generating explainability traces"""
    
    def __init__(self, db: Session):
        self.db = db
        self.signal_service = PersonaSignalService(db)
        self.location_service = LocationAffinityService(db)
    
    def generate_trace(
        self,
        user_id: int,
        target_id: str,
        target_type: str,
        persona_id: Optional[int] = None
    ) -> TargetTrace:
        """
        Generate a trace for a target (company or persona).
        
        Args:
            user_id: User ID
            target_id: Target ID (company ID or persona ID)
            target_type: "company" or "persona"
            persona_id: Persona ID (if matching from persona perspective)
        
        Returns:
            TargetTrace: Generated trace with full explanation
        """
        ***REMOVED*** Get target data
        if target_type == "company":
            target = self.db.query(Company).filter(Company.id == int(target_id)).first()
            if not target or target.user_id != user_id:
                raise ValueError(f"Company with ID {target_id} not found")
        elif target_type == "persona":
            target = self.db.query(Persona).filter(Persona.id == int(target_id)).first()
            if not target or target.user_id != user_id:
                raise ValueError(f"Persona with ID {target_id} not found")
        else:
            raise ValueError(f"Invalid target_type: {target_type}")
        
        ***REMOVED*** Get persona if provided (for matching perspective)
        persona = None
        if persona_id:
            persona = self.db.query(Persona).filter(
                Persona.id == persona_id,
                Persona.user_id == user_id
            ).first()
            if not persona:
                raise ValueError(f"Persona with ID {persona_id} not found")
        
        ***REMOVED*** Generate signals used
        signals_used = self._extract_signals_used(target, target_type, persona)
        
        ***REMOVED*** Get signal weights
        signal_weights = self._get_signal_weights(user_id, persona_id)
        
        ***REMOVED*** Get signal exclusions
        signal_exclusions = self._get_signal_exclusions(user_id, persona_id, signals_used)
        
        ***REMOVED*** Calculate location affinity
        location_affinity_score, location_affinity_details = self._calculate_location_affinity(
            target, target_type, persona
        )
        
        ***REMOVED*** Calculate overall score
        overall_score = self._calculate_overall_score(
            signals_used,
            signal_weights,
            location_affinity_score
        )
        
        ***REMOVED*** Calculate confidence levels
        confidence_level, confidence_breakdown = self._calculate_confidence(
            signals_used,
            location_affinity_details
        )
        
        ***REMOVED*** Create or update trace
        existing_trace = self.db.query(TargetTrace).filter(
            TargetTrace.user_id == user_id,
            TargetTrace.target_id == target_id,
            TargetTrace.target_type == target_type,
            TargetTrace.persona_id == persona_id
        ).first()
        
        if existing_trace:
            ***REMOVED*** Update existing trace
            existing_trace.overall_score = overall_score
            existing_trace.signals_used = signals_used
            existing_trace.signal_weights = signal_weights
            existing_trace.signal_exclusions = signal_exclusions
            existing_trace.location_affinity_score = location_affinity_score
            existing_trace.location_affinity_details = location_affinity_details
            existing_trace.confidence_level = confidence_level
            existing_trace.confidence_breakdown = confidence_breakdown
            self.db.commit()
            self.db.refresh(existing_trace)
            return existing_trace
        else:
            ***REMOVED*** Create new trace
            new_trace = TargetTrace(
                user_id=user_id,
                target_id=target_id,
                target_type=target_type,
                persona_id=persona_id,
                overall_score=overall_score,
                signals_used=signals_used,
                signal_weights=signal_weights,
                signal_exclusions=signal_exclusions,
                location_affinity_score=location_affinity_score,
                location_affinity_details=location_affinity_details,
                confidence_level=confidence_level,
                confidence_breakdown=confidence_breakdown
            )
            self.db.add(new_trace)
            self.db.commit()
            self.db.refresh(new_trace)
            return new_trace
    
    def _extract_signals_used(
        self,
        target: Any,
        target_type: str,
        persona: Optional[Persona]
    ) -> List[Dict[str, Any]]:
        """Extract signals from target"""
        signals = []
        
        if target_type == "company":
            ***REMOVED*** Company signals
            if hasattr(target, 'industry') and target.industry:
                signals.append({
                    "signal_type": "industry",
                    "signal_value": target.industry,
                    "weight": 1.0,  ***REMOVED*** Will be updated with actual weight
                    "contribution": 0.0,  ***REMOVED*** Will be calculated
                    "confidence": "high"
                })
            
            if hasattr(target, 'location_data') and target.location_data:
                location = target.location_data
                if isinstance(location, dict):
                    city = location.get("city") or location.get("address", "").split(",")[0] if location.get("address") else None
                    if city:
                        signals.append({
                            "signal_type": "location",
                            "signal_value": city,
                            "weight": 1.0,
                            "contribution": 0.0,
                            "confidence": "high"
                        })
        
        elif target_type == "persona":
            ***REMOVED*** Persona signals
            if hasattr(target, 'job_title') and target.job_title:
                signals.append({
                    "signal_type": "job_title",
                    "signal_value": target.job_title,
                    "weight": 1.0,
                    "contribution": 0.0,
                    "confidence": "medium"
                })
            
            if hasattr(target, 'department') and target.department:
                signals.append({
                    "signal_type": "department",
                    "signal_value": target.department,
                    "weight": 1.0,
                    "contribution": 0.0,
                    "confidence": "medium"
                })
            
            if hasattr(target, 'work_location') and target.work_location:
                location = target.work_location
                if isinstance(location, dict):
                    city = location.get("city") or location.get("address", "").split(",")[0] if location.get("address") else None
                    if city:
                        signals.append({
                            "signal_type": "location",
                            "signal_value": city,
                            "weight": 1.0,
                            "contribution": 0.0,
                            "confidence": "high"
                        })
        
        return signals
    
    def _get_signal_weights(
        self,
        user_id: int,
        persona_id: Optional[int]
    ) -> Dict[str, float]:
        """Get effective signal weights"""
        weights = {}
        
        ***REMOVED*** Get all weights (persona-specific or global)
        all_weights = self.signal_service.get_all_weights(user_id, persona_id=persona_id)
        
        for weight_obj in all_weights:
            weights[weight_obj.signal_type] = weight_obj.weight
        
        return weights
    
    def _get_signal_exclusions(
        self,
        user_id: int,
        persona_id: Optional[int],
        signals_used: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Get signal exclusions and check if they apply"""
        exclusions = []
        
        ***REMOVED*** Get all exclusions
        all_exclusions = self.signal_service.get_all_exclusions(user_id, persona_id=persona_id)
        
        ***REMOVED*** Check each signal against exclusions
        for signal in signals_used:
            signal_type = signal["signal_type"]
            signal_value = signal["signal_value"]
            
            ***REMOVED*** Check if this signal value is excluded
            is_excluded = self.signal_service.is_signal_excluded(
                user_id, signal_type, signal_value, persona_id
            )
            
            exclusions.append({
                "signal_type": signal_type,
                "signal_value": signal_value,
                "excluded": is_excluded
            })
        
        return exclusions
    
    def _calculate_location_affinity(
        self,
        target: Any,
        target_type: str,
        persona: Optional[Persona]
    ) -> Tuple[Optional[float], Optional[Dict[str, Any]]]:
        """Calculate location affinity if persona has location configured"""
        if not persona or not persona.work_location:
            return None, None
        
        persona_lat = persona.work_location.get("latitude")
        persona_lng = persona.work_location.get("longitude")
        
        if persona_lat is None or persona_lng is None:
            return None, None
        
        ***REMOVED*** Get target location
        target_lat = None
        target_lng = None
        target_signals = None
        
        if target_type == "company":
            if hasattr(target, 'location_data') and target.location_data:
                location = target.location_data
                if isinstance(location, dict):
                    target_lat = location.get("latitude")
                    target_lng = location.get("longitude")
        elif target_type == "persona":
            if hasattr(target, 'work_location') and target.work_location:
                location = target.work_location
                if isinstance(location, dict):
                    target_lat = location.get("latitude")
                    target_lng = location.get("longitude")
            if hasattr(target, 'location_signals'):
                target_signals = target.location_signals
        
        if target_lat is None or target_lng is None:
            return None, None
        
        ***REMOVED*** Calculate affinity score
        score = self.location_service.calculate_location_affinity_score(
            persona_lat=persona_lat,
            persona_lng=persona_lng,
            persona_signals=persona.location_signals or [],
            persona_radius=persona.location_radius_meters,
            persona_polygon=persona.location_polygon,
            target_lat=target_lat,
            target_lng=target_lng,
            target_signals=target_signals
        )
        
        ***REMOVED*** Calculate distance
        distance_km = self.location_service._haversine_distance(
            persona_lat, persona_lng, target_lat, target_lng
        )
        
        ***REMOVED*** Check if within radius/polygon
        within_radius = False
        within_polygon = False
        
        if persona.location_radius_meters:
            within_radius = (distance_km * 1000) <= persona.location_radius_meters
        
        if persona.location_polygon:
            within_polygon = self.location_service._point_in_polygon(
                target_lat, target_lng, persona.location_polygon
            )
        
        ***REMOVED*** Check signal match
        signal_match = False
        matching_signals = []
        if persona.location_signals and target_signals:
            matching_signals = list(set(persona.location_signals) & set(target_signals))
            signal_match = len(matching_signals) > 0
        
        details = {
            "score": score,
            "distance_km": round(distance_km, 2),
            "within_radius": within_radius,
            "within_polygon": within_polygon,
            "signal_match": signal_match,
            "matching_signals": matching_signals
        }
        
        return score, details
    
    def _calculate_overall_score(
        self,
        signals_used: List[Dict[str, Any]],
        signal_weights: Dict[str, float],
        location_affinity_score: Optional[float]
    ) -> float:
        """Calculate overall matching score"""
        if not signals_used:
            return 0.0
        
        ***REMOVED*** Apply weights to signals
        weighted_contributions = []
        total_weight = 0.0
        
        for signal in signals_used:
            signal_type = signal["signal_type"]
            weight = signal_weights.get(signal_type, 1.0)
            signal["weight"] = weight
            
            ***REMOVED*** Calculate contribution (simplified - would be more sophisticated in production)
            contribution = weight / len(signals_used)
            signal["contribution"] = contribution
            weighted_contributions.append(contribution)
            total_weight += weight
        
        ***REMOVED*** Normalize contributions
        if total_weight > 0:
            for signal in signals_used:
                signal["contribution"] = signal["contribution"] / (total_weight / len(signals_used))
        
        ***REMOVED*** Calculate base score from signals
        base_score = sum(weighted_contributions) / len(weighted_contributions) if weighted_contributions else 0.0
        
        ***REMOVED*** Incorporate location affinity (30% weight)
        if location_affinity_score is not None:
            overall_score = (base_score * 0.7) + (location_affinity_score * 0.3)
        else:
            overall_score = base_score
        
        return min(1.0, max(0.0, overall_score))
    
    def _calculate_confidence(
        self,
        signals_used: List[Dict[str, Any]],
        location_affinity_details: Optional[Dict[str, Any]]
    ) -> Tuple[str, Dict[str, str]]:
        """Calculate confidence levels"""
        confidence_breakdown = {}
        
        ***REMOVED*** Per-signal confidence
        for signal in signals_used:
            signal_type = signal["signal_type"]
            confidence_breakdown[signal_type] = signal.get("confidence", "medium")
        
        ***REMOVED*** Location confidence
        if location_affinity_details:
            location_conf = "high" if location_affinity_details.get("within_radius") or location_affinity_details.get("within_polygon") else "medium"
            confidence_breakdown["location"] = location_conf
        
        ***REMOVED*** Overall confidence (average of all confidences)
        if confidence_breakdown:
            high_count = sum(1 for c in confidence_breakdown.values() if c == "high")
            medium_count = sum(1 for c in confidence_breakdown.values() if c == "medium")
            
            if high_count >= len(confidence_breakdown) * 0.7:
                overall_confidence = "high"
            elif high_count + medium_count >= len(confidence_breakdown) * 0.5:
                overall_confidence = "medium"
            else:
                overall_confidence = "low"
        else:
            overall_confidence = "medium"
        
        confidence_breakdown["overall"] = overall_confidence
        
        return overall_confidence, confidence_breakdown
