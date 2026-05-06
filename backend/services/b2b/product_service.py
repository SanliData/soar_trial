***REMOVED*** -*- coding: utf-8 -*-
"""
Product Service - Product definition and management
"""

from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.b2b_product import Product
from backend.db import SessionLocal
import os
from backend.services.openai_client import OpenAIVisionClient


class ProductService:
    """Product definition and management service"""
    
    def __init__(self):
        self.openai_client = OpenAIVisionClient() if os.getenv("OPENAI_API_KEY") else None
    
    def _get_db(self) -> Session:
        """Get database session"""
        return SessionLocal()
    
    def create_product(
        self,
        user_id: str,
        name: str,
        description: Optional[str] = None,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Product:
        """Create new product"""
        db = self._get_db()
        try:
            product = Product(
                user_id=user_id,
                name=name,
                description=description,
                category=category,
                subcategory=subcategory,
                status="draft",
                metadata=metadata or {},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(product)
            db.commit()
            db.refresh(product)
            
            return product
        finally:
            db.close()
    
    def understand_product(self, product_id: int) -> Product:
        """
        Analyze product using AI to understand:
        - Product category and use cases
        - Target industries
        - Product features
        """
        db = self._get_db()
        try:
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise ValueError("Product not found")
            
            ***REMOVED*** Build prompt for AI analysis
            prompt = f"""
            Analyze this product and provide:
            1. Product category and subcategory
            2. List of use cases (where/how it's used)
            3. Target industries that use this product (e.g., for "yeast" -> bakeries, pastry shops, burger restaurants)
            4. Key product features
            
            Product Name: {product.name}
            Description: {product.description or 'N/A'}
            
            Return JSON format:
            {{
                "category": "...",
                "subcategory": "...",
                "use_cases": ["...", "..."],
                "target_industries": ["...", "..."],
                "product_features": ["...", "..."]
            }}
            """
            
            ***REMOVED*** Call OpenAI for analysis
            if self.openai_client:
                try:
                    response = self.openai_client.analyze_text(prompt)
                    ai_result = response.get("metadata", {})
                except Exception as e:
                    print(f"OpenAI analysis error: {e}")
                    ai_result = {}
            else:
                ***REMOVED*** Fallback: Basic analysis without AI
                ai_result = self._basic_product_analysis(product)
            
            ***REMOVED*** Update product with AI analysis
            product.ai_analysis = ai_result
            product.use_cases = ai_result.get("use_cases", [])
            product.target_industries = ai_result.get("target_industries", [])
            product.product_features = ai_result.get("product_features", [])
            product.category = ai_result.get("category") or product.category
            product.subcategory = ai_result.get("subcategory") or product.subcategory
            product.status = "analyzed"
            product.analyzed_at = datetime.utcnow()
            product.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(product)
            
            return product
        finally:
            db.close()
    
    def _basic_product_analysis(self, product: Product) -> Dict:
        """Basic product analysis without AI (fallback)"""
        ***REMOVED*** Simple keyword-based analysis
        name_lower = product.name.lower()
        description_lower = (product.description or "").lower()
        text = f"{name_lower} {description_lower}"
        
        ***REMOVED*** Industry keywords mapping
        industry_keywords = {
            "bakery": ["yeast", "flour", "dough", "bread", "bakery"],
            "restaurant": ["food", "ingredient", "cooking"],
            "manufacturing": ["material", "component", "production"],
            "retail": ["consumer", "retail", "store"],
        }
        
        detected_industries = []
        for industry, keywords in industry_keywords.items():
            if any(kw in text for kw in keywords):
                detected_industries.append(industry)
        
        return {
            "category": "general",
            "subcategory": "unknown",
            "use_cases": [f"Used in {industry}" for industry in detected_industries],
            "target_industries": detected_industries or ["general"],
            "product_features": []
        }
    
    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        db = self._get_db()
        try:
            return db.query(Product).filter(Product.id == product_id).first()
        finally:
            db.close()
    
    def get_products_by_user(self, user_id: str) -> List[Product]:
        """Get products by user"""
        db = self._get_db()
        try:
            return db.query(Product).filter(Product.user_id == user_id).all()
        finally:
            db.close()
    
    def update_product(self, product_id: int, **kwargs) -> Optional[Product]:
        """Update product information"""
        db = self._get_db()
        try:
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product:
                return None
            
            for key, value in kwargs.items():
                if hasattr(product, key) and value is not None:
                    setattr(product, key, value)
            
            product.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(product)
            
            return product
        finally:
            db.close()


***REMOVED*** Global instance
product_service = ProductService()

