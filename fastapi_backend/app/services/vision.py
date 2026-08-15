import io
import os
import logging
from PIL import Image
import easyocr
import google.generativeai as genai

logger = logging.getLogger(__name__)

class VisionService:
    def __init__(self):
        # 1. Initialize EasyOCR Reader for English and Hindi on CPU (gpu=False)
        # This keeps local VRAM usage at 0 for OCR, running entirely on system RAM/CPU.
        logger.info("Initializing local EasyOCR reader for ['en', 'hi']...")
        try:
            self.ocr_reader = easyocr.Reader(['en', 'hi'], gpu=False)
            logger.info("EasyOCR reader initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR reader: {e}")
            self.ocr_reader = None

        # 2. Initialize Gemini API Client for visual analysis (rash/injury description)
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
        if self.gemini_api_key:
            logger.info("Configuring Google Generative AI client with GEMINI_API_KEY...")
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.cloud_model = genai.GenerativeModel('gemini-2.0-flash')
                logger.info("Google Generative AI client configured successfully.")
            except Exception as e:
                logger.error(f"Failed to configure Google Generative AI client: {e}")
                self.cloud_model = None
        else:
            logger.warning("GEMINI_API_KEY environment variable is not set. Cloud vision tasks will fail.")
            self.cloud_model = None

    async def process_image(self, file_bytes: bytes, filename: str, is_document: bool) -> str:
        """
        Processes an image upload.
        If is_document is True, runs local EasyOCR on CPU.
        If is_document is False, runs Cloud Gemini Flash API.
        """
        # Validate that we have valid image bytes
        try:
            image = Image.open(io.BytesIO(file_bytes))
            image.verify() # Verify it is a valid PIL Image
            # Re-open because verify() consumes the file stream
            image = Image.open(io.BytesIO(file_bytes))
        except Exception as e:
            logger.error(f"Uploaded file '{filename}' is not a valid image: {e}")
            raise ValueError("Invalid image file provided.")

        # --- PATH A: Local Document OCR ---
        if is_document:
            if not self.ocr_reader:
                logger.error("EasyOCR reader is not initialized.")
                raise RuntimeError("OCR service is currently unavailable.")
            
            logger.info(f"Processing '{filename}' as a document using local EasyOCR...")
            try:
                # EasyOCR readtext can accept a PIL Image directly
                results = self.ocr_reader.readtext(image)
                # Combine detected text lines
                extracted_text = " ".join([text for (_, text, _) in results])
                
                if not extracted_text.strip():
                    return "No text could be detected in the uploaded document."
                
                return extracted_text.strip()
            except Exception as e:
                logger.error(f"Error running local EasyOCR on '{filename}': {e}")
                raise RuntimeError(f"OCR processing failed: {str(e)}")

        # --- PATH B: Cloud Image/Photo Description ---
        else:
            if not self.cloud_model:
                logger.error("Cloud vision model (Gemini) is not configured.")
                raise RuntimeError("Cloud vision analysis is unavailable. Make sure GEMINI_API_KEY is set.")

            logger.info(f"Processing '{filename}' as a photograph/medical image using Gemini Cloud VLM...")
            try:
                prompt = (
                    "You are a medical visual assistant. Look at the provided image and give a professional, "
                    "objective description of its contents. If it shows a skin rash, lesion, injury, swelling, "
                    "or clinical condition, describe it carefully (color, shape, margins, texture, approximate location). "
                    "Do not provide a definitive diagnosis; instead, describe what is visible and suggest consulting a "
                    "healthcare provider if necessary. Provide your description in English."
                )
                
                # Gemini SDK accepts a PIL Image object directly along with a prompt list
                response = self.cloud_model.generate_content([prompt, image])
                return response.text.strip()
            except Exception as e:
                logger.error(f"Error calling Gemini API for '{filename}': {e}")
                raise RuntimeError(f"Cloud vision analysis failed: {str(e)}")
