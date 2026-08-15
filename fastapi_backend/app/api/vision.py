import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from app.services.vision import VisionService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/vision",
    tags=["Vision Service"]
)

# Instantiate the service as a singleton to ensure models (EasyOCR) are loaded
# only once at application startup, rather than on every HTTP request.
logger.info("Initializing VisionService singleton for API Router...")
vision_service = VisionService()

def get_vision_service() -> VisionService:
    return vision_service

@router.post("/analyze", status_code=status.HTTP_200_OK)
async def analyze_image(
    file: UploadFile = File(..., description="The image file to analyze (PNG, JPEG, etc.)"),
    is_document: bool = Query(
        False, 
        description="Set to True if the image is a document/prescription/handwritten note (runs local EasyOCR). "
                    "Set to False if it is a photograph of a rash/injury (runs Cloud VLM)."
    ),
    service: VisionService = Depends(get_vision_service)
):
    """
    Upload an image for analysis.
    
    - **is_document = False (Default)**: Automatically describes visual clinical symptoms, rashes, scans, or injuries using Google Gemini VLM in the cloud.
    - **is_document = True**: Performs high-accuracy optical character recognition (OCR) on handwritten notes, tables, charts, or documents using local EasyOCR on the CPU.
    """
    # 1. Basic extension/content type check
    allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/webp"]
    if file.content_type not in allowed_types:
        logger.warning(f"Rejected upload of unsupported content type '{file.content_type}' for file '{file.filename}'")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed formats: PNG, JPEG, JPG, WEBP."
        )

    try:
        # 2. Read the image file bytes
        file_bytes = await file.read()
        
        # 3. Process the image using the Vision Service
        result_text = await service.process_image(
            file_bytes=file_bytes,
            filename=file.filename,
            is_document=is_document
        )
        
        return {
            "status": "Success",
            "filename": file.filename,
            "is_document": is_document,
            "analysis": result_text
        }

    except ValueError as val_err:
        logger.error(f"Validation error processing image: {val_err}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )
    except Exception as err:
        logger.error(f"Error handling image analysis: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image analysis failed: {str(err)}"
        )
