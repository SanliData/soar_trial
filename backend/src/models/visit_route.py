"""
MODEL: visit_route
PURPOSE: Physical visit route planning for field sales
ENCODING: UTF-8 WITHOUT BOM

Max 20 visits per route.
Google Maps compatible output.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Index, Float
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime, JSON
from sqlalchemy.orm import relationship
from src.db.base import Base


class VisitRoute(Base):
    """
    Visit route for field sales.
    Geographic optimization, persona density priority.
    """
    
    __tablename__ = "visit_routes"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign key to PlanResult
    plan_result_id = Column(Integer, ForeignKey("plan_results.id"), nullable=False, index=True)
    
    # Route information
    route_name = Column(String(255), nullable=True)   # User-provided route name
    region = Column(String(255), nullable=False)   # Geographic region
    
    # Route status
    status = Column(String(50), default="pending", nullable=False, index=True)   # pending, optimized, ready, completed
    
    # Optimization parameters
    max_stops = Column(Integer, default=20, nullable=False)   # Hard limit: 20 stops per route
    optimization_priority = Column(String(50), default="geographic", nullable=False)   # geographic, persona_density, mixed
    
    # Route data (stops)
    stops = Column(JSON, nullable=True)   # List of stops with address, time window, priority
    
    # Geographic data
    total_distance_km = Column(Float, nullable=True)
    estimated_duration_hours = Column(Float, nullable=True)
    
    # Google Maps compatibility
    google_maps_url = Column(String(1024), nullable=True)   # Generated Google Maps route URL
    google_maps_embed_url = Column(String(1024), nullable=True)   # Embed URL for iframe
    
    # Export files
    csv_file_path = Column(String(512), nullable=True)
    pdf_file_path = Column(String(512), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    optimized_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    plan_result = relationship("PlanResult", backref="visit_routes")
    stops_list = relationship("VisitStop", back_populates="route", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_visit_route_result_id', 'plan_result_id'),
        Index('idx_visit_route_status', 'status'),
    )


class VisitStop(Base):
    """
    Individual stop in a visit route.
    """
    
    __tablename__ = "visit_stops"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign key to VisitRoute
    route_id = Column(Integer, ForeignKey("visit_routes.id"), nullable=False, index=True)
    
    # Stop information
    stop_order = Column(Integer, nullable=False)   # Order in route (1, 2, 3, ...)
    business_name = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)
    
    # Location coordinates
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Time window
    suggested_time_window = Column(String(100), nullable=True)   # e.g., "10:00-11:30"
    suggested_date = Column(String(50), nullable=True)   # Optional: suggested date
    
    # Priority and scoring
    priority_score = Column(Float, nullable=True)   # 0.0 - 1.0, based on persona density and relevance
    persona_count = Column(Integer, default=0, nullable=False)   # Number of target personas at this location
    
    # Additional metadata (renamed from 'metadata' to avoid SQLAlchemy reserved name conflict)
    meta_data = Column("metadata", JSON, nullable=True)   # Additional business info, notes, etc.
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationship
    route = relationship("VisitRoute", back_populates="stops_list")
    
    # Indexes
    __table_args__ = (
        Index('idx_visit_stop_route_id', 'route_id'),
        Index('idx_visit_stop_order', 'route_id', 'stop_order'),
    )
