"""
ROUTER: product_router
PURPOSE: Product definition and barcode/QR code reading
ENCODING: UTF-8 WITHOUT BOM
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import base64
from io import BytesIO

try:
    from pyzbar import pyzbar
    from PIL import Image
    BARCODE_AVAILABLE = True
except ImportError:
    BARCODE_AVAILABLE = False

from src.services.vision_service import get_vision_service

router = APIRouter(prefix="/products", tags=["products"])


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    identification_type: str  ***REMOVED*** "name", "barcode", "qrcode", "giftcode"
    code: Optional[str] = None


class ProductResponse(BaseModel):
    product_id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    identification_type: str
    code: Optional[str] = None
    status: str


class BarcodeReadResponse(BaseModel):
    success: bool
    code_type: Optional[str] = None  ***REMOVED*** "barcode", "qrcode"
    data: Optional[str] = None
    error: Optional[str] = None


class ImageSearchResponse(BaseModel):
    success: bool
    product_matches: Optional[list] = None
    detected_text: Optional[str] = None
    ai_analysis: Optional[dict] = None
    error: Optional[str] = None


class VisionAnalysisResponse(BaseModel):
    success: bool
    objects: Optional[List[dict]] = None
    text: Optional[str] = None
    labels: Optional[List[dict]] = None
    product_info: Optional[dict] = None
    error: Optional[str] = None


@router.post("/read-barcode", response_model=BarcodeReadResponse)
async def read_barcode(file: UploadFile = File(...)):
    """
    Read barcode or QR code from uploaded image.
    Supports: EAN-13, UPC-A, Code128, QR Code, DataMatrix, etc.
    """
    if not BARCODE_AVAILABLE:
        return BarcodeReadResponse(
            success=False,
            error="Barcode reading library not available. Install: pip install pyzbar pillow"
        )
    
    try:
        ***REMOVED*** Read image file
        contents = await file.read()
        image = Image.open(BytesIO(contents))
        
        ***REMOVED*** Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        ***REMOVED*** Read barcodes/QR codes
        barcodes = pyzbar.decode(image)
        
        if not barcodes:
            return BarcodeReadResponse(
                success=False,
                error="No barcode or QR code found in image"
            )
        
        ***REMOVED*** Get first barcode/QR code
        barcode = barcodes[0]
        code_type = "qrcode" if barcode.type == "QRCODE" else "barcode"
        data = barcode.data.decode('utf-8')
        
        return BarcodeReadResponse(
            success=True,
            code_type=code_type,
            data=data
        )
        
    except Exception as e:
        return BarcodeReadResponse(
            success=False,
            error=f"Error reading barcode: {str(e)}"
        )


@router.post("/create", response_model=ProductResponse)
async def create_product(product: ProductCreate):
    """
    Create a new product definition.
    """
    import uuid
    
    product_id = str(uuid.uuid4())
    
    return ProductResponse(
        product_id=product_id,
        name=product.name,
        description=product.description,
        category=product.category,
        identification_type=product.identification_type,
        code=product.code,
        status="created"
    )


@router.post("/search-by-image", response_model=ImageSearchResponse)
async def search_by_image(file: UploadFile = File(...)):
    """
    Search for product by uploading an image.
    Uses OCR and AI analysis to identify the product.
    """
    try:
        ***REMOVED*** Read image file
        contents = await file.read()
        image = Image.open(BytesIO(contents))
        
        ***REMOVED*** Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        ***REMOVED*** Try to read barcode/QR code first
        barcodes = []
        if BARCODE_AVAILABLE:
            try:
                barcodes = pyzbar.decode(image)
            except:
                pass
        
        detected_text = ""
        product_matches = []
        
        ***REMOVED*** If barcode found, use it for search
        if barcodes:
            barcode = barcodes[0]
            code_data = barcode.data.decode('utf-8')
            detected_text = f"Barcode/QR Code: {code_data}"
            product_matches.append({
                "type": "barcode_match",
                "code": code_data,
                "code_type": "qrcode" if barcode.type == "QRCODE" else "barcode",
                "confidence": 0.95
            })
        
        ***REMOVED*** AI Analysis (mock for now - can be enhanced with actual AI)
        ai_analysis = {
            "detected_objects": ["product", "packaging"],
            "estimated_category": "unknown",
            "confidence": 0.7,
            "suggestions": [
                "Check product name in image",
                "Verify barcode/QR code if visible",
                "Review product description"
            ]
        }
        
        ***REMOVED*** Try to extract text from image (basic OCR simulation)
        ***REMOVED*** In production, use actual OCR service
        detected_text += " | Image uploaded for analysis"
        
        return ImageSearchResponse(
            success=True,
            product_matches=product_matches,
            detected_text=detected_text,
            ai_analysis=ai_analysis
        )
        
    except Exception as e:
        return ImageSearchResponse(
            success=False,
            error=f"Error processing image: {str(e)}"
        )


@router.post("/analyze-vision", response_model=VisionAnalysisResponse)
async def analyze_image_vision(file: UploadFile = File(...)):
    """
    Analyze image using Google Cloud Vision API.
    Performs object detection, OCR (text extraction), and labeling.
    """
    vision_service = get_vision_service()
    
    if not vision_service.is_available():
        return VisionAnalysisResponse(
            success=False,
            error="Google Cloud Vision API is not available. Please install google-cloud-vision and configure credentials."
        )
    
    try:
        ***REMOVED*** Read image file
        contents = await file.read()
        
        ***REMOVED*** Analyze image with Vision API
        analysis = vision_service.analyze_product_image(contents)
        
        if not analysis.get("success"):
            return VisionAnalysisResponse(
                success=False,
                error=analysis.get("error", "Unknown error during analysis")
            )
        
        raw_analysis = analysis.get("raw_analysis", {})
        
        return VisionAnalysisResponse(
            success=True,
            objects=raw_analysis.get("objects", []),
            text=raw_analysis.get("text", ""),
            labels=raw_analysis.get("labels", []),
            product_info={
                "product_name": analysis.get("product_name", ""),
                "category": analysis.get("category", ""),
                "barcode_text": analysis.get("barcode_text", ""),
                "description": analysis.get("description", ""),
                "confidence": analysis.get("confidence", 0.0)
            }
        )
        
    except Exception as e:
        return VisionAnalysisResponse(
            success=False,
            error=f"Error processing image: {str(e)}"
        )


@router.post("/analyze-vision-detailed", response_model=VisionAnalysisResponse)
async def analyze_image_vision_detailed(
    file: UploadFile = File(...),
    features: Optional[str] = "all"
):
    """
    Analyze image with detailed Vision API features.
    
    Features: "objects", "text", "labels", or "all"
    """
    vision_service = get_vision_service()
    
    if not vision_service.is_available():
        return VisionAnalysisResponse(
            success=False,
            error="Google Cloud Vision API is not available."
        )
    
    try:
        contents = await file.read()
        
        feature_list = [f.strip() for f in features.split(",")] if features else ["all"]
        analysis = vision_service.analyze_image(contents, features=feature_list)
        
        if not analysis.get("success"):
            return VisionAnalysisResponse(
                success=False,
                error=analysis.get("error", "Unknown error")
            )
        
        return VisionAnalysisResponse(
            success=True,
            objects=analysis.get("objects", []),
            text=analysis.get("text", ""),
            labels=analysis.get("labels", [])
        )
        
    except Exception as e:
        return VisionAnalysisResponse(
            success=False,
            error=f"Error: {str(e)}"
        )


@router.get("/health")
def health():
    vision_service = get_vision_service()
    return {
        "status": "ok",
        "domain": "products",
        "barcode_available": BARCODE_AVAILABLE,
        "vision_api_available": vision_service.is_available()
    }

