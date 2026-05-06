"""
SERVICE: persona_signal_service
PURPOSE: Service for managing signal weights and exclusions in Living Persona Engine
ENCODING: UTF-8 WITHOUT BOM
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.models.persona_signal_weight import PersonaSignalWeight
from src.models.persona_signal_exclusion import PersonaSignalExclusion
from src.models.persona import Persona


class PersonaSignalService:
    """Service for managing signal weights and exclusions"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========================================================================
    # SIGNAL WEIGHTING
    # ========================================================================
    
    def get_signal_weight(
        self,
        user_id: int,
        signal_type: str,
        persona_id: Optional[int] = None
    ) -> Optional[PersonaSignalWeight]:
        """
        Get signal weight with fallback logic:
        1. Persona-specific weight (if persona_id provided)
        2. Global weight (user-level)
        3. Default weight (1.0) if none found
        """
        # Try persona-specific first
        if persona_id:
            weight = self.db.query(PersonaSignalWeight).filter(
                and_(
                    PersonaSignalWeight.user_id == user_id,
                    PersonaSignalWeight.persona_id == persona_id,
                    PersonaSignalWeight.signal_type == signal_type,
                    PersonaSignalWeight.is_active == True
                )
            ).first()
            
            if weight:
                return weight
        
        # Fall back to global weight
        global_weight = self.db.query(PersonaSignalWeight).filter(
            and_(
                PersonaSignalWeight.user_id == user_id,
                PersonaSignalWeight.persona_id == None,
                PersonaSignalWeight.signal_type == signal_type,
                PersonaSignalWeight.is_active == True
            )
        ).first()
        
        return global_weight
    
    def get_effective_weight(
        self,
        user_id: int,
        signal_type: str,
        persona_id: Optional[int] = None
    ) -> float:
        """
        Get effective weight (actual numeric value, not model object).
        Returns default 1.0 if no weight found.
        """
        weight_obj = self.get_signal_weight(user_id, signal_type, persona_id)
        return weight_obj.weight if weight_obj else 1.0
    
    def get_all_weights(
        self,
        user_id: int,
        persona_id: Optional[int] = None
    ) -> List[PersonaSignalWeight]:
        """Get all signal weights for a user/persona"""
        query = self.db.query(PersonaSignalWeight).filter(
            PersonaSignalWeight.user_id == user_id,
            PersonaSignalWeight.is_active == True
        )
        
        if persona_id is not None:
            # Get persona-specific weights
            query = query.filter(PersonaSignalWeight.persona_id == persona_id)
        else:
            # Get global weights only
            query = query.filter(PersonaSignalWeight.persona_id == None)
        
        return query.all()
    
    def set_signal_weight(
        self,
        user_id: int,
        signal_type: str,
        weight: float,
        persona_id: Optional[int] = None,
        description: Optional[str] = None
    ) -> PersonaSignalWeight:
        """
        Set signal weight. Creates or updates existing weight.
        
        Args:
            user_id: User ID
            signal_type: Signal type (e.g., "location", "industry")
            weight: Weight value (0.0 to 10.0)
            persona_id: Persona ID (None for global weight)
            description: Optional description
        """
        # Validate weight range
        if weight < 0.0 or weight > 10.0:
            raise ValueError("Weight must be between 0.0 and 10.0")
        
        # Check if persona exists (if persona_id provided)
        if persona_id:
            persona = self.db.query(Persona).filter(Persona.id == persona_id).first()
            if not persona:
                raise ValueError(f"Persona with ID {persona_id} not found")
            if persona.user_id != user_id:
                raise ValueError("Persona does not belong to user")
        
        # Find existing weight
        existing = self.db.query(PersonaSignalWeight).filter(
            and_(
                PersonaSignalWeight.user_id == user_id,
                PersonaSignalWeight.persona_id == persona_id,
                PersonaSignalWeight.signal_type == signal_type
            )
        ).first()
        
        if existing:
            # Update existing
            existing.weight = weight
            existing.description = description
            existing.is_active = True
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            # Create new
            new_weight = PersonaSignalWeight(
                user_id=user_id,
                persona_id=persona_id,
                signal_type=signal_type,
                weight=weight,
                description=description,
                is_active=True
            )
            self.db.add(new_weight)
            self.db.commit()
            self.db.refresh(new_weight)
            return new_weight
    
    def delete_signal_weight(
        self,
        user_id: int,
        weight_id: int
    ) -> bool:
        """Delete (deactivate) a signal weight"""
        weight = self.db.query(PersonaSignalWeight).filter(
            and_(
                PersonaSignalWeight.id == weight_id,
                PersonaSignalWeight.user_id == user_id
            )
        ).first()
        
        if not weight:
            return False
        
        weight.is_active = False
        self.db.commit()
        return True
    
    # ========================================================================
    # SIGNAL EXCLUSION
    # ========================================================================
    
    def is_signal_excluded(
        self,
        user_id: int,
        signal_type: str,
        signal_value: str,
        persona_id: Optional[int] = None
    ) -> bool:
        """
        Check if a signal value is excluded.
        Checks both persona-specific and global exclusions.
        """
        # Check persona-specific exclusion first
        if persona_id:
            exclusion = self.db.query(PersonaSignalExclusion).filter(
                and_(
                    PersonaSignalExclusion.user_id == user_id,
                    PersonaSignalExclusion.persona_id == persona_id,
                    PersonaSignalExclusion.signal_type == signal_type,
                    PersonaSignalExclusion.signal_value == signal_value,
                    PersonaSignalExclusion.is_active == True
                )
            ).first()
            
            if exclusion:
                return True
        
        # Check global exclusion
        global_exclusion = self.db.query(PersonaSignalExclusion).filter(
            and_(
                PersonaSignalExclusion.user_id == user_id,
                PersonaSignalExclusion.persona_id == None,
                PersonaSignalExclusion.signal_type == signal_type,
                PersonaSignalExclusion.signal_value == signal_value,
                PersonaSignalExclusion.is_active == True
            )
        ).first()
        
        return global_exclusion is not None
    
    def get_all_exclusions(
        self,
        user_id: int,
        persona_id: Optional[int] = None
    ) -> List[PersonaSignalExclusion]:
        """Get all signal exclusions for a user/persona"""
        query = self.db.query(PersonaSignalExclusion).filter(
            PersonaSignalExclusion.user_id == user_id,
            PersonaSignalExclusion.is_active == True
        )
        
        if persona_id is not None:
            # Get persona-specific exclusions
            query = query.filter(PersonaSignalExclusion.persona_id == persona_id)
        else:
            # Get global exclusions only
            query = query.filter(PersonaSignalExclusion.persona_id == None)
        
        return query.all()
    
    def add_signal_exclusion(
        self,
        user_id: int,
        signal_type: str,
        signal_value: str,
        persona_id: Optional[int] = None,
        exclusion_reason: Optional[str] = None
    ) -> PersonaSignalExclusion:
        """
        Add signal exclusion. Creates new exclusion if not exists.
        
        Args:
            user_id: User ID
            signal_type: Signal type (e.g., "location", "industry")
            signal_value: Signal value to exclude (e.g., "Retail", "Istanbul")
            persona_id: Persona ID (None for global exclusion)
            exclusion_reason: Optional reason
        """
        # Check if persona exists (if persona_id provided)
        if persona_id:
            persona = self.db.query(Persona).filter(Persona.id == persona_id).first()
            if not persona:
                raise ValueError(f"Persona with ID {persona_id} not found")
            if persona.user_id != user_id:
                raise ValueError("Persona does not belong to user")
        
        # Check if exclusion already exists
        existing = self.db.query(PersonaSignalExclusion).filter(
            and_(
                PersonaSignalExclusion.user_id == user_id,
                PersonaSignalExclusion.persona_id == persona_id,
                PersonaSignalExclusion.signal_type == signal_type,
                PersonaSignalExclusion.signal_value == signal_value
            )
        ).first()
        
        if existing:
            # Reactivate if deactivated
            existing.is_active = True
            existing.exclusion_reason = exclusion_reason
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            # Create new
            new_exclusion = PersonaSignalExclusion(
                user_id=user_id,
                persona_id=persona_id,
                signal_type=signal_type,
                signal_value=signal_value,
                exclusion_reason=exclusion_reason,
                is_active=True
            )
            self.db.add(new_exclusion)
            self.db.commit()
            self.db.refresh(new_exclusion)
            return new_exclusion
    
    def remove_signal_exclusion(
        self,
        user_id: int,
        exclusion_id: int
    ) -> bool:
        """Remove (deactivate) a signal exclusion"""
        exclusion = self.db.query(PersonaSignalExclusion).filter(
            and_(
                PersonaSignalExclusion.id == exclusion_id,
                PersonaSignalExclusion.user_id == user_id
            )
        ).first()
        
        if not exclusion:
            return False
        
        exclusion.is_active = False
        self.db.commit()
        return True
    
    def get_all_effective_config(
        self,
        user_id: int,
        persona_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get all effective signal configuration (weights + exclusions) for a user/persona.
        Returns a dictionary with weights and exclusions.
        """
        weights = self.get_all_weights(user_id, persona_id)
        exclusions = self.get_all_exclusions(user_id, persona_id)
        
        return {
            "weights": {w.signal_type: w.to_dict() for w in weights},
            "exclusions": [e.to_dict() for e in exclusions]
        }
