"""
SERVICE: vision_service
PURPOSE: Google Cloud Vision API integration for image analysis
ENCODING: UTF-8 WITHOUT BOM
"""

import os
from typing import Dict, List, Optional, Any
from io import BytesIO
from PIL import Image

try:
    from google.cloud import vision
    from google.cloud.vision_v1 import types
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False


class VisionService:
    """
    Service for Google Cloud Vision API operations.
    Provides object detection, OCR, and labeling capabilities.
    """
    
    def __init__(self):
        """Initialize Vision Service with Google Cloud Vision client."""
        self.client = None
        if VISION_AVAILABLE:
            try:
                # Initialize client - uses GOOGLE_APPLICATION_CREDENTIALS env var or default credentials
                self.client = vision.ImageAnnotatorClient()
            except Exception as e:
                print(f"Warning: Could not initialize Vision API client: {e}")
                self.client = None
    
    def is_available(self) -> bool:
        """Check if Vision API is available and configured."""
        return VISION_AVAILABLE and self.client is not None
    
    def analyze_image(
        self,
        image_content: bytes,
        features: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze image using Google Cloud Vision API.
        
        Args:
            image_content: Image file content as bytes
            features: List of features to extract. Options:
                - "objects": Object detection
                - "text": OCR (text detection)
                - "labels": Label detection
                - "all": All features (default)
        
        Returns:
            Dictionary containing:
                - success: bool
                - objects: List of detected objects
                - text: Detected text (OCR)
                - labels: List of labels with confidence scores
                - error: Error message if any
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Google Cloud Vision API is not available. Please install google-cloud-vision and configure credentials."
            }
        
        if features is None:
            features = ["all"]
        
        try:
            # Create image object
            image = vision.Image(content=image_content)
            
            # Prepare feature requests
            feature_requests = []
            
            if "all" in features or "objects" in features:
                feature_requests.append(
                    types.Feature(type_=types.Feature.Type.OBJECT_LOCALIZATION, max_results=50)
                )
            
            if "all" in features or "text" in features:
                feature_requests.append(
                    types.Feature(type_=types.Feature.Type.TEXT_DETECTION, max_results=10)
                )
                feature_requests.append(
                    types.Feature(type_=types.Feature.Type.DOCUMENT_TEXT_DETECTION, max_results=1)
                )
            
            if "all" in features or "labels" in features:
                feature_requests.append(
                    types.Feature(type_=types.Feature.Type.LABEL_DETECTION, max_results=20)
                )
            
            # Perform batch annotation
            request = types.AnnotateImageRequest(
                image=image,
                features=feature_requests
            )
            
            response = self.client.annotate_image(request=request)
            
            # Parse results
            result = {
                "success": True,
                "objects": [],
                "text": "",
                "labels": [],
                "full_text_annotation": None
            }
            
            # Extract objects
            if response.localized_object_annotations:
                for obj in response.localized_object_annotations:
                    result["objects"].append({
                        "name": obj.name,
                        "score": obj.score,
                        "mid": obj.mid,
                        "bounding_poly": [
                            {"x": vertex.x, "y": vertex.y}
                            for vertex in obj.bounding_poly.normalized_vertices
                        ]
                    })
            
            # Extract text (OCR)
            detected_texts = []
            if response.text_annotations:
                # First annotation is the full text
                if len(response.text_annotations) > 0:
                    full_text = response.text_annotations[0].description
                    result["full_text_annotation"] = full_text
                    detected_texts.append(full_text)
            
            # Also check document text detection
            if response.full_text_annotation:
                result["full_text_annotation"] = response.full_text_annotation.text
            
            result["text"] = "\n".join(detected_texts) if detected_texts else ""
            
            # Extract labels
            if response.label_annotations:
                for label in response.label_annotations:
                    result["labels"].append({
                        "description": label.description,
                        "score": label.score,
                        "mid": label.mid,
                        "topicality": label.topicality
                    })
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error analyzing image: {str(e)}"
            }
    
    def detect_objects(self, image_content: bytes) -> Dict[str, Any]:
        """
        Detect objects in image.
        
        Args:
            image_content: Image file content as bytes
        
        Returns:
            Dictionary with detected objects
        """
        return self.analyze_image(image_content, features=["objects"])
    
    def extract_text(self, image_content: bytes) -> Dict[str, Any]:
        """
        Extract text from image using OCR.
        
        Args:
            image_content: Image file content as bytes
        
        Returns:
            Dictionary with extracted text
        """
        return self.analyze_image(image_content, features=["text"])
    
    def detect_labels(self, image_content: bytes) -> Dict[str, Any]:
        """
        Detect labels/categories in image.
        
        Args:
            image_content: Image file content as bytes
        
        Returns:
            Dictionary with detected labels
        """
        return self.analyze_image(image_content, features=["labels"])
    
    def analyze_product_image(self, image_content: bytes) -> Dict[str, Any]:
        """
        Analyze product image with all features for product identification.
        
        Args:
            image_content: Image file content as bytes
        
        Returns:
            Dictionary with comprehensive product analysis:
                - product_name: Extracted product name
                - category: Detected category
                - barcode_text: Text that might be barcode
                - description: Product description from labels
                - confidence: Overall confidence score
        """
        analysis = self.analyze_image(image_content, features=["all"])
        
        if not analysis.get("success"):
            return analysis
        
        # Extract product information
        product_info = {
            "success": True,
            "product_name": "",
            "category": "",
            "barcode_text": "",
            "description": "",
            "confidence": 0.0,
            "raw_analysis": analysis
        }
        
        # Try to extract product name from text
        text = analysis.get("text", "").strip()
        if text:
            # Look for product name patterns (first line, capitalized words, etc.)
            lines = text.split("\n")
            if lines:
                # First non-empty line might be product name
                for line in lines[:5]:   # Check first 5 lines
                    line = line.strip()
                    if line and len(line) > 3 and len(line) < 100:
                        product_info["product_name"] = line
                        break
        
        # Extract category from labels
        labels = analysis.get("labels", [])
        if labels:
            # Get highest confidence label as category
            top_label = labels[0] if labels else None
            if top_label and top_label.get("score", 0) > 0.7:
                product_info["category"] = top_label.get("description", "")
                product_info["confidence"] = top_label.get("score", 0)
        
        # Look for barcode-like text (numeric sequences)
        if text:
            import re
            # Look for long numeric sequences (potential barcodes)
            barcode_pattern = r'\b\d{8,}\b'
            matches = re.findall(barcode_pattern, text)
            if matches:
                product_info["barcode_text"] = matches[0]
        
        # Build description from labels
        if labels:
            descriptions = [label.get("description", "") for label in labels[:5]]
            product_info["description"] = ", ".join(descriptions)
        
        return product_info


# Singleton instance
_vision_service_instance = None


def get_vision_service() -> VisionService:
    """Get or create VisionService singleton instance."""
    global _vision_service_instance
    if _vision_service_instance is None:
        _vision_service_instance = VisionService()
    return _vision_service_instance


