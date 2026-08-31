import io
import os
import logging
from PIL import Image

logger = logging.getLogger(__name__)

class VisionService:
    def __init__(self):
        # We lazily load models to reduce FastAPI startup time.
        self._ocr_reader = None
        self._gemini_client = None
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")

    def _get_ocr_reader(self):
        if self._ocr_reader is None:
            logger.info("Lazily initializing local EasyOCR reader for ['en', 'hi']...")
            try:
                # Import EasyOCR (and PyTorch) only when needed!
                import easyocr
                self._ocr_reader = easyocr.Reader(['en', 'hi'], gpu=False)
                logger.info("EasyOCR reader initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize EasyOCR reader: {e}")
                raise RuntimeError("OCR service is currently unavailable.")
        return self._ocr_reader

    def _get_gemini_client(self):
        if self._gemini_client is None:
            if not self.gemini_api_key:
                logger.error("GEMINI_API_KEY environment variable is not set. Cloud vision tasks will fail.")
                raise RuntimeError("Cloud vision analysis is unavailable. Make sure GEMINI_API_KEY is set.")
            
            logger.info("Lazily configuring Google Generative AI client...")
            try:
                from google import genai
                self._gemini_client = genai.Client(api_key=self.gemini_api_key)
                logger.info("Google Generative AI client configured successfully.")
            except Exception as e:
                logger.error(f"Failed to configure Google Generative AI client: {e}")
                raise RuntimeError("Cloud vision analysis failed to initialize.")
        return self._gemini_client

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
            ocr_reader = self._get_ocr_reader()
            
            logger.info(f"Processing '{filename}' as a document using local EasyOCR...")
            try:
                # EasyOCR readtext can accept a PIL Image directly
                results = ocr_reader.readtext(image)
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
            gemini_client = self._get_gemini_client()

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
                response = gemini_client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=[prompt, image]
                )
                return response.text.strip()
            except Exception as e:
                logger.error(f"Error calling Gemini API for '{filename}': {e}")
                raise RuntimeError(f"Cloud vision analysis failed: {str(e)}")
