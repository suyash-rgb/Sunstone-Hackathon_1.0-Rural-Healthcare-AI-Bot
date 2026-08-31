from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.translation_service import TranslationService

router = APIRouter(
    prefix="/translation",
    tags=["Translation Service"]
)

# Instantiate the service globally so the model is cached across requests
translation_service = TranslationService()

class TranslationRequest(BaseModel):
    text: str
    src_lang: str
    tgt_lang: str

class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    src_lang: str
    tgt_lang: str

@router.post("/", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")
    
    try:
        translated = await translation_service.translate(
            text=request.text,
            src_lang=request.src_lang,
            tgt_lang=request.tgt_lang
        )
        return TranslationResponse(
            original_text=request.text,
            translated_text=translated,
            src_lang=request.src_lang,
            tgt_lang=request.tgt_lang
        )
    except ValueError as ve:
        # Client-side errors (like unsupported language)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # Server-side errors
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")
