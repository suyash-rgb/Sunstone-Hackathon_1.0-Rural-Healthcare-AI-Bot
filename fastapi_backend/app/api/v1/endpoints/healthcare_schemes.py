from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.services.healthcare_schemes_service import HealthCareSchemesService
from app.schemas.health_scheme import (
    HealthSchemeDetailResponse, HealthSchemePaginatedResponse,
    RAGSearchRequest, RAGSearchResponse
) 

router = APIRouter(prefix="/healthcare-schemes", tags=["Health Scheme Discovery"]) 

@router.get("", response_model=HealthSchemePaginatedResponse)
async def get_health_schemes(
    state: Optional[str] = Query(None, description="Filter by State/UT or Pan India"),
    level: Optional[str] = Query(None, description="Filter by Level (Central / State / State/ UT)"),
    category: Optional[str] = Query(None, description="Filter by Category keyword"),
    search: Optional[str] = Query(None, description="Search query across scheme name, tags, description"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_session)
):
    """Retrieve paginated health schemes with filter options."""
    return await HealthCareSchemesService.get_schemes_paginated(
        db=db, state=state, level=level, category=category,
        search=search, page=page, limit=limit
    )

@router.get("/meta/states", response_model=List[str])
async def get_available_states(db: AsyncSession = Depends(get_session)):
    """List all available distinct states/UTs."""
    return await HealthCareSchemesService.get_available_states(db=db)

@router.get("/meta/categories", response_model=List[str])
async def get_available_categories(db: AsyncSession = Depends(get_session)):
    """List all unique scheme categories."""
    return await HealthCareSchemesService.get_available_categories(db=db)

@router.get("/{id_or_slug}", response_model=HealthSchemeDetailResponse)
async def get_scheme_detail(id_or_slug: str, db: AsyncSession = Depends(get_session)):
    """Retrieve full scheme detail by internal ID or slug."""
    scheme = await HealthCareSchemesService.get_scheme_by_id_or_slug(db=db, id_or_slug=id_or_slug)
    if not scheme:
        raise HTTPException(status_code=404, detail="Health scheme not found")
    return scheme

@router.post("/rag/search", response_model=RAGSearchResponse)
async def rag_hybrid_search(
    req: RAGSearchRequest,
    db: AsyncSession = Depends(get_session)
):
    """Perform hybrid vector & relational search and generate Groq AI answer."""
    return await HealthCareSchemesService.perform_rag_hybrid_search(
        db=db, user_query=req.query, state=req.state, top_k=req.top_k
    )
