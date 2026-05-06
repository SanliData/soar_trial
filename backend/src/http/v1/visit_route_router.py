"""
ROUTER: visit_route_router
PURPOSE: Visit route generation endpoints
ENCODING: UTF-8 WITHOUT BOM

Max 20 stops per route.
Google Maps compatible.
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.http.v1.b2b_api_router import validate_api_key
from src.services.visit_route_service import get_visit_route_service
from src.services.result_service import get_result_service
from src.core.query_limits import MAX_VISIT_STOPS_PER_ROUTE

logger = logging.getLogger(__name__)

router = APIRouter(tags=["visit_route"])


***REMOVED*** Request Models
class CreateRouteRequest(BaseModel):
    plan_result_id: int
    region: str
    max_stops: Optional[int] = Field(None, description=f"Max stops (default: {MAX_VISIT_STOPS_PER_ROUTE}, hard limit: {MAX_VISIT_STOPS_PER_ROUTE})")
    optimization_priority: Optional[str] = Field("geographic", description="geographic, persona_density, mixed")


class GenerateStopsRequest(BaseModel):
    businesses: List[Dict[str, Any]] = Field(..., description="List of businesses with address, coordinates, persona_count")


***REMOVED*** Response Models
class RouteResponse(BaseModel):
    route_id: int
    plan_result_id: int
    region: str
    status: str
    max_stops: int
    stops_count: int
    google_maps_url: Optional[str] = None
    created_at: str


***REMOVED*** Endpoints
@router.post("/route", response_model=RouteResponse)
async def create_visit_route(
    request: CreateRouteRequest,
    api_key: str = Depends(validate_api_key),
    db: Session = Depends(get_db)
):
    """
    Create a new visit route.
    Max 20 stops per route (hard limit).
    """
    try:
        ***REMOVED*** Validate plan result exists
        result_service = get_result_service(db)
        plan_result = result_service.get_result_hub(request.plan_result_id)
        if not plan_result:
            raise HTTPException(status_code=404, detail=f"Plan result {request.plan_result_id} not found")
        
        ***REMOVED*** Enforce max_stops limit
        max_stops = request.max_stops if request.max_stops else MAX_VISIT_STOPS_PER_ROUTE
        if max_stops > MAX_VISIT_STOPS_PER_ROUTE:
            max_stops = MAX_VISIT_STOPS_PER_ROUTE
        
        visit_service = get_visit_route_service(db)
        route = visit_service.create_visit_route(
            plan_result_id=request.plan_result_id,
            region=request.region,
            max_stops=max_stops,
            optimization_priority=request.optimization_priority or "geographic"
        )
        
        return RouteResponse(
            route_id=route.id,
            plan_result_id=route.plan_result_id,
            region=route.region,
            status=route.status,
            max_stops=route.max_stops,
            stops_count=0,
            google_maps_url=route.google_maps_url,
            created_at=route.created_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating route: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create route")


@router.post("/route/{route_id}/generate-stops")
async def generate_route_stops(
    route_id: int,
    request: GenerateStopsRequest,
    api_key: str = Depends(validate_api_key),
    db: Session = Depends(get_db)
):
    """
    Generate optimized route stops from businesses.
    Businesses are automatically limited to max_stops (20).
    """
    try:
        visit_service = get_visit_route_service(db)
        route = visit_service.get_route(route_id)
        
        if not route:
            raise HTTPException(status_code=404, detail=f"Route {route_id} not found")
        
        ***REMOVED*** Generate stops (automatically limited to route.max_stops)
        stops = visit_service.generate_route_stops(route_id, request.businesses)
        
        ***REMOVED*** Refresh route to get updated data
        route = visit_service.get_route(route_id)
        
        return {
            "route_id": route_id,
            "status": route.status,
            "stops_count": len(stops),
            "google_maps_url": route.google_maps_url,
            "stops": [
                {
                    "order": stop.stop_order,
                    "business_name": stop.business_name,
                    "address": stop.address,
                    "latitude": stop.latitude,
                    "longitude": stop.longitude,
                    "priority_score": stop.priority_score,
                    "persona_count": stop.persona_count
                }
                for stop in stops
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating stops: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate stops")


@router.get("/route/{route_id}")
async def get_route(
    route_id: int,
    api_key: str = Depends(validate_api_key),
    db: Session = Depends(get_db)
):
    """
    Get visit route details including stops and Google Maps URL.
    """
    try:
        visit_service = get_visit_route_service(db)
        route = visit_service.get_route(route_id)
        
        if not route:
            raise HTTPException(status_code=404, detail=f"Route {route_id} not found")
        
        stops_data = [
            {
                "order": stop.stop_order,
                "business_name": stop.business_name,
                "address": stop.address,
                "latitude": stop.latitude,
                "longitude": stop.longitude,
                "suggested_time_window": stop.suggested_time_window,
                "priority_score": stop.priority_score,
                "persona_count": stop.persona_count
            }
            for stop in route.visit_stops_list
        ]
        
        return {
            "route_id": route.id,
            "plan_result_id": route.plan_result_id,
            "region": route.region,
            "status": route.status,
            "max_stops": route.max_stops,
            "stops_count": len(stops_data),
            "total_distance_km": route.total_distance_km,
            "estimated_duration_hours": route.estimated_duration_hours,
            "google_maps_url": route.google_maps_url,
            "google_maps_embed_url": route.google_maps_embed_url,
            "stops": stops_data,
            "created_at": route.created_at.isoformat(),
            "optimized_at": route.optimized_at.isoformat() if route.optimized_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting route: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get route")


@router.get("/plans/{plan_id}/routes")
async def get_routes_for_plan(
    plan_id: str,
    api_key: str = Depends(validate_api_key),
    db: Session = Depends(get_db)
):
    """
    Get all visit routes for a plan.
    """
    try:
        result_service = get_result_service(db)
        plan_result = result_service.get_result_hub(plan_id)
        
        if not plan_result:
            raise HTTPException(status_code=404, detail=f"Plan result not found for plan {plan_id}")
        
        visit_service = get_visit_route_service(db)
        routes = visit_service.get_routes_for_plan(plan_result.id)
        
        return {
            "plan_id": plan_id,
            "routes": [
                {
                    "route_id": route.id,
                    "region": route.region,
                    "status": route.status,
                    "max_stops": route.max_stops,
                    "stops_count": len(route.visit_stops_list) if route.visit_stops_list else 0,
                    "google_maps_url": route.google_maps_url,
                    "created_at": route.created_at.isoformat()
                }
                for route in routes
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting routes: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get routes")
