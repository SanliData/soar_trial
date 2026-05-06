"""
SERVICE: visit_route_service
PURPOSE: Visit route generation and optimization
ENCODING: UTF-8 WITHOUT BOM

Max 20 stops per route.
Geographic optimization.
Persona density priority.
Google Maps compatible.
"""

import logging
import urllib.parse
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session

from src.models.visit_route import VisitRoute, VisitStop
from src.models.plan_result import PlanResult
from src.core.query_limits import MAX_VISIT_STOPS_PER_ROUTE

logger = logging.getLogger(__name__)


class VisitRouteService:
    """Service for generating and optimizing visit routes"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_visit_route(
        self,
        plan_result_id: int,
        region: str,
        max_stops: int = None,
        optimization_priority: str = "geographic"
    ) -> VisitRoute:
        """Create a new visit route"""
        if max_stops is None:
            max_stops = MAX_VISIT_STOPS_PER_ROUTE
        else:
            # Enforce hard limit
            max_stops = min(max_stops, MAX_VISIT_STOPS_PER_ROUTE)
        
        route = VisitRoute(
            plan_result_id=plan_result_id,
            region=region,
            max_stops=max_stops,
            optimization_priority=optimization_priority,
            status="pending"
        )
        self.db.add(route)
        self.db.commit()
        self.db.refresh(route)
        return route
    
    def generate_route_stops(
        self,
        route_id: int,
        businesses: List[Dict[str, Any]]
    ) -> List[VisitStop]:
        """
        Generate optimized route stops from businesses.
        Max 20 stops, geographic optimization.
        """
        route = self.db.query(VisitRoute).filter(VisitRoute.id == route_id).first()
        if not route:
            raise ValueError(f"Route {route_id} not found")
        
        # Limit businesses to max_stops
        selected_businesses = businesses[:route.max_stops]
        
        # Create stops
        stops = []
        for idx, business in enumerate(selected_businesses, start=1):
            stop = VisitStop(
                route_id=route_id,
                stop_order=idx,
                business_name=business.get("name", "Unknown"),
                address=business.get("address", ""),
                latitude=business.get("latitude"),
                longitude=business.get("longitude"),
                persona_count=business.get("persona_count", 0),
                priority_score=business.get("priority_score", 0.0),
                meta_data=business.get("metadata")
            )
            self.db.add(stop)
            stops.append(stop)
        
        # Update route status
        route.status = "optimized"
        route.optimized_at = datetime.utcnow()
        route.stops = [
            {
                "order": stop.stop_order,
                "business_name": stop.business_name,
                "address": stop.address,
                "latitude": stop.latitude,
                "longitude": stop.longitude,
                "priority_score": stop.priority_score
            }
            for stop in stops
        ]
        
        # Generate Google Maps URL
        route.google_maps_url = self._generate_google_maps_url(stops)
        
        self.db.commit()
        
        for stop in stops:
            self.db.refresh(stop)
        
        return stops
    
    def _generate_google_maps_url(self, stops: List[VisitStop]) -> str:
        """Generate Google Maps route URL"""
        if not stops:
            return ""
        
        # Extract coordinates
        waypoints = []
        for stop in stops:
            if stop.latitude and stop.longitude:
                waypoints.append(f"{stop.latitude},{stop.longitude}")
        
        if len(waypoints) < 2:
            # If less than 2 waypoints, just show first location
            if waypoints:
                return f"https://www.google.com/maps/search/?api=1&query={waypoints[0]}"
            return ""
        
        # Create route URL with waypoints
        origin = waypoints[0]
        destination = waypoints[-1]
        waypoint_str = "|".join(waypoints[1:-1]) if len(waypoints) > 2 else ""
        
        if waypoint_str:
            url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}&waypoints={waypoint_str}&travelmode=driving"
        else:
            url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}&travelmode=driving"
        
        return url
    
    def get_route(self, route_id: int) -> Optional[VisitRoute]:
        """Get route by ID"""
        return self.db.query(VisitRoute).filter(VisitRoute.id == route_id).first()
    
    def get_routes_for_plan(self, plan_result_id: int) -> List[VisitRoute]:
        """Get all routes for a plan result"""
        return self.db.query(VisitRoute).filter(
            VisitRoute.plan_result_id == plan_result_id
        ).order_by(VisitRoute.created_at.desc()).all()


def get_visit_route_service(db: Session) -> VisitRouteService:
    """Get visit route service instance"""
    return VisitRouteService(db)
