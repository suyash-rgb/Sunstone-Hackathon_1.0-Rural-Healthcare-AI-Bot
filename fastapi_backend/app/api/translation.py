from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.translation import TranslationService

router = APIRouter(
    prefix="/translation",
    tags=["Translation Service"]
)

# Instantiate the service globally so the model is cached across requests
translation_service = TranslationService()

class TranslationRequest(BaseModel):
    text: str
    src_lang: str = "eng_Latn"
    tgt_lang: str = "hin_Deva"

class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    src_lang: str
    tgt_lang: str

@router.post("/", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
