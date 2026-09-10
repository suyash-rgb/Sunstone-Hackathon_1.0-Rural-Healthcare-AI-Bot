from typing import List, Optional
from pydantic import BaseModel, ConfigDict
import datetime

class FAQResponse(BaseModel):
    id: int
    question_number: int
    question: str
    answer: str

    model_config = ConfigDict(from_attributes=True)

class ReferenceResponse(BaseModel):
    id: int
    title: Optional[str] = None
    url: str

    model_config = ConfigDict(from_attributes=True)

class DocumentResponse(BaseModel):
    id: int
    document_name: str

    model_config = ConfigDict(from_attributes=True)

class HealthSchemeResponse(BaseModel):
    id: int
    scheme_id: Optional[str] = None
    slug: str
    scheme_name: str
    short_title: Optional[str] = None
    state: str
    department: Optional[str] = None
    level: str
    categories: Optional[str] = None
    subcategories: Optional[str] = None
    tags: Optional[str] = None
    beneficiaries: Optional[str] = None
    brief_description: Optional[str] = None
    benefits: Optional[str] = None
    eligibility: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class HealthSchemeDetailResponse(HealthSchemeResponse):
    description: Optional[str] = None
    application_process: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    
    faqs: List[FAQResponse] = []
    references: List[ReferenceResponse] = []
    documents: List[DocumentResponse] = []

    model_config = ConfigDict(from_attributes=True)

class HealthSchemePaginatedResponse(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    items: List[HealthSchemeResponse]

class RAGSearchRequest(BaseModel):
    query: str
    state: Optional[str] = None
    top_k: int = 4

class RAGChunkResponse(BaseModel):
    scheme_id: int
    scheme_name: str
    state: str
    chunk_type: str
    chunk_text: str
    score: float

class RAGSearchResponse(BaseModel):
    query: str
    answer: str
    retrieved_chunks: List[RAGChunkResponse]
