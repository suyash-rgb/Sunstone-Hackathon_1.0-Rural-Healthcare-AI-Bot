from dotenv import load_dotenv
load_dotenv()
import os
import math
import numpy as np
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func, or_, text
from fastembed import TextEmbedding
import groq

from app.db.models.health_scheme import (
    HealthScheme, HealthSchemeFAQ, HealthSchemeReference,
    HealthSchemeDocument, HealthSchemeEmbedding
)
from app.schemas.health_scheme import (
    HealthSchemePaginatedResponse, HealthSchemeResponse,
    HealthSchemeDetailResponse, RAGSearchResponse, RAGChunkResponse
)

# Lazy-loaded FastEmbed model
_embed_model = None

def get_embed_model():
    global _embed_model
    if _embed_model is None:
        _embed_model = TextEmbedding()
    return _embed_model

def cosine_sim(a: List[float], b: List[float]) -> float:
    a_arr = np.array(a, dtype=np.float32)
    b_arr = np.array(b, dtype=np.float32)
    norm_a = np.linalg.norm(a_arr)
    norm_b = np.linalg.norm(b_arr)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a_arr, b_arr) / (norm_a * norm_b))

class HealthSchemesService:

    @staticmethod
    async def get_schemes_paginated(
        db: AsyncSession,
        state: Optional[str] = None,
        level: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ) -> HealthSchemePaginatedResponse:
        query = select(HealthScheme)

        if state:
            query = query.filter(or_(HealthScheme.state.ilike(f"%{state}%"), HealthScheme.state == "Pan India"))
        if level:
            query = query.filter(HealthScheme.level == level)
        if category:
            query = query.filter(HealthScheme.categories.ilike(f"%{category}%"))
        if search:
            search_filter = or_(
                HealthScheme.scheme_name.ilike(f"%{search}%"),
                HealthScheme.tags.ilike(f"%{search}%"),
                HealthScheme.brief_description.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)

        # Total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Pagination
        offset = (page - 1) * limit
        query = query.order_by(HealthScheme.id.asc()).offset(offset).limit(limit)
        result = await db.execute(query)
        items = result.scalars().all()

        total_pages = math.ceil(total / limit) if total > 0 else 1

        return HealthSchemePaginatedResponse(
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
            items=items
        )

    @staticmethod
    async def get_available_states(db: AsyncSession) -> List[str]:
        query = select(HealthScheme.state).distinct().order_by(HealthScheme.state.asc())
        result = await db.execute(query)
        states = [r for r in result.scalars().all() if r]
        return states

    @staticmethod
    async def get_available_categories(db: AsyncSession) -> List[str]:
        query = select(HealthScheme.categories)
        result = await db.execute(query)
        raw_cats = result.scalars().all()
        categories_set = set()
        for cat_str in raw_cats:
            if cat_str:
                for item in cat_str.split(","):
                    item_clean = item.strip()
                    if item_clean:
                        categories_set.add(item_clean)
        return sorted(list(categories_set))

    @staticmethod
    async def get_scheme_by_id_or_slug(db: AsyncSession, id_or_slug: str) -> Optional[HealthScheme]:
        if id_or_slug.isdigit():
            query = select(HealthScheme)\
                .options(selectinload(HealthScheme.faqs), selectinload(HealthScheme.references), selectinload(HealthScheme.documents))\
                .filter(HealthScheme.id == int(id_or_slug))
        else:
            query = select(HealthScheme)\
                .options(selectinload(HealthScheme.faqs), selectinload(HealthScheme.references), selectinload(HealthScheme.documents))\
                .filter(HealthScheme.slug == id_or_slug)

        result = await db.execute(query)
        return result.scalars().first()

    @staticmethod
    async def perform_rag_hybrid_search(
        db: AsyncSession,
        user_query: str,
        state: Optional[str] = None,
        top_k: int = 4
    ) -> RAGSearchResponse:
        embed_model = get_embed_model()
        query_vec = list(embed_model.embed([user_query]))[0].tolist()

        emb_query = select(HealthSchemeEmbedding, HealthScheme.scheme_name, HealthScheme.state)\
            .join(HealthScheme, HealthScheme.id == HealthSchemeEmbedding.scheme_id)

        if state:
            emb_query = emb_query.filter(or_(HealthScheme.state.ilike(f"%{state}%"), HealthScheme.state == "Pan India"))
        else:
            emb_query = emb_query.filter(HealthScheme.level == 'Central')

        res = await db.execute(emb_query)
        rows = res.all()

        scored_chunks = []
        for emb_obj, scheme_name, scheme_state in rows:
            if emb_obj.embedding:
                score = cosine_sim(query_vec, emb_obj.embedding)
                scored_chunks.append((score, emb_obj, scheme_name, scheme_state))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        
        # Diversity filter: maximum 1 chunk per scheme to ensure we retrieve top_k distinct schemes
        top_items = []
        seen_schemes = set()
        for item in scored_chunks:
            emb_obj = item[1]
            if emb_obj.scheme_id not in seen_schemes:
                top_items.append(item)
                seen_schemes.add(emb_obj.scheme_id)
            if len(top_items) >= top_k:
                break

        retrieved_chunks = []
        context_passages = []

        for score, emb_obj, scheme_name, scheme_state in top_items:
            retrieved_chunks.append(RAGChunkResponse(
                scheme_id=emb_obj.scheme_id,
                scheme_name=scheme_name,
                state=scheme_state,
                chunk_type=emb_obj.chunk_type,
                chunk_text=emb_obj.chunk_text,
                score=round(score, 4)
            ))
            context_passages.append(f"--- Scheme Context ({scheme_name} | {scheme_state}) ---\n{emb_obj.chunk_text}")

        context_str = "\n\n".join(context_passages)

        groq_api_key = os.environ.get("FASTAPI_GROK_API_KEY") or os.environ.get("GROQ_API_KEY") or ""
        groq_model = os.environ.get("FASTAPI_GROK_MODEL")
        llm_answer = ""

        if groq_api_key:
            try:
                client = groq.Groq(api_key=groq_api_key)
                prompt = f"""You are ArogyaMitra, a knowledgeable and compassionate rural healthcare AI assistant.
Answer the user's question accurately using ONLY the retrieved government health scheme context below.
Start your answer directly by naming the most relevant scheme(s), followed by detailed guidance on eligibility, benefits, and application steps.

RETRIEVED SCHEMES CONTEXT:
{context_str}

USER QUESTION:
{user_query}
"""
                response = client.chat.completions.create(
                    model=groq_model,
                    messages=[
                        {"role": "system", "content": "You are ArogyaMitra, an empathetic rural healthcare AI bot. Always structure your responses starting with the scheme name in bold, followed by clear eligibility and benefit points."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=600
                )
                llm_answer = response.choices[0].message.content.strip()
            except Exception as e:
                top_scheme = retrieved_chunks[0].scheme_name if retrieved_chunks else "Unknown Scheme"
                llm_answer = f"**{top_scheme}**\n\nRetrieved top relevant schemes based on your query:\n\n" + "\n\n".join([f"• **{c.scheme_name}** ({c.state}):\n{c.chunk_text}" for c in retrieved_chunks[:2]])
        else:
            top_scheme = retrieved_chunks[0].scheme_name if retrieved_chunks else "Unknown Scheme"
            llm_answer = f"**{top_scheme}**\n\nRelevant Health Schemes:\n\n" + "\n\n".join([f"• **{c.scheme_name}** ({c.state}):\n{c.chunk_text}" for c in retrieved_chunks[:2]])

        return RAGSearchResponse(
            query=user_query,
            answer=llm_answer,
            retrieved_chunks=retrieved_chunks
        )
