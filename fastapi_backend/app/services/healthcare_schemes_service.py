from dotenv import load_dotenv
load_dotenv()
import os
import math
import re
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

STOP_WORDS = {
    "a", "an", "the", "in", "on", "at", "to", "for", "of", "with", "by", "from",
    "up", "about", "into", "over", "after", "and", "or", "but", "is", "are",
    "was", "were", "be", "been", "being", "have", "has", "had", "do", "does",
    "did", "will", "would", "shall", "should", "may", "might", "must", "can",
    "could", "this", "that", "these", "those", "my", "your", "his", "her",
    "its", "our", "their", "what", "which", "who", "whom", "whose", "where",
    "when", "why", "how", "all", "any", "both", "each", "few", "more", "most",
    "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so",
    "than", "too", "very", "site", "area", "like", "know", "want", "launch",
    "launched", "scheme", "schemes", "government", "india", "state", "national",
    "department", "project", "mission", "center", "centre", "detail", "details"
}

class HealthCareSchemesService:

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
    @staticmethod
    async def perform_rag_hybrid_search(
        db: AsyncSession,
        user_query: str,
        state: Optional[str] = None,
        top_k: int = 4,
        min_score: float = 0.58
    ) -> RAGSearchResponse:
        embed_model = get_embed_model()
        query_vec = list(embed_model.embed([user_query]))[0].tolist()

        emb_query = select(HealthSchemeEmbedding, HealthScheme.scheme_name, HealthScheme.state)\
            .join(HealthScheme, HealthScheme.id == HealthSchemeEmbedding.scheme_id)

        if state:
            emb_query = emb_query.filter(or_(HealthScheme.state.ilike(f"%{state}%"), HealthScheme.state == "Pan India"))
        else:
            emb_query = emb_query.filter(or_(HealthScheme.level == 'Central', HealthScheme.state == 'Pan India'))

        res = await db.execute(emb_query)
        rows = res.all()

        if not rows:
            return RAGSearchResponse(
                query=user_query,
                answer="No relevant health schemes found for your query criteria.",
                retrieved_chunks=[]
            )

        # 1. Dense Vector Search & Similarity Thresholding
        vector_scored = []
        for emb_obj, scheme_name, scheme_state in rows:
            if emb_obj.embedding:
                score = cosine_sim(query_vec, emb_obj.embedding)
                if score >= min_score:
                    vector_scored.append((score, emb_obj, scheme_name, scheme_state))

        vector_scored.sort(key=lambda x: x[0], reverse=True)
        vector_ranks = {item[1].id: rank + 1 for rank, item in enumerate(vector_scored)}

        # 2. Sparse Lexical Search (Filtered Keyword Match)
        query_terms = set(t.lower() for t in re.findall(r'\w+', user_query) if len(t) > 2 and t.lower() not in STOP_WORDS)
        
        lexical_scored = []
        if query_terms:
            for emb_obj, scheme_name, scheme_state in rows:
                text_lower = emb_obj.chunk_text.lower()
                match_count = sum(1 for term in query_terms if re.search(r'\b' + re.escape(term) + r'\b', text_lower))
                if match_count > 0:
                    lexical_scored.append((match_count, emb_obj, scheme_name, scheme_state))

            lexical_scored.sort(key=lambda x: x[0], reverse=True)

        lexical_ranks = {item[1].id: rank + 1 for rank, item in enumerate(lexical_scored)}

        # 3. Reciprocal Rank Fusion (RRF)
        rrf_k = 60
        combined_chunks = {}

        all_candidates = set(vector_ranks.keys()) | {item[1].id for item in lexical_scored if item[0] >= 2}
        emb_map = {emb_obj.id: (emb_obj, scheme_name, scheme_state) for emb_obj, scheme_name, scheme_state in rows}

        for emb_id in all_candidates:
            v_rank = vector_ranks.get(emb_id, None)
            l_rank = lexical_ranks.get(emb_id, None)

            v_rrf = (1.0 / (rrf_k + v_rank)) if v_rank is not None else 0.0
            l_rrf = (1.0 / (rrf_k + l_rank)) if l_rank is not None else 0.0
            rrf_score = v_rrf + l_rrf

            v_score = 0.0
            for item in vector_scored:
                if item[1].id == emb_id:
                    v_score = item[0]
                    break

            emb_obj, scheme_name, scheme_state = emb_map[emb_id]
            combined_chunks[emb_id] = (rrf_score, v_score, emb_obj, scheme_name, scheme_state)

        # Sort by final RRF score
        sorted_rrf = sorted(combined_chunks.values(), key=lambda x: x[0], reverse=True)

        # 4. Diversity Filter: Select top 1 scheme up to top_k, prioritizing Metadata chunk for context
        top_items = []
        seen_schemes = set()
        
        # Build map of metadata chunks for fast lookup
        metadata_map = {}
        for emb_obj, scheme_name, scheme_state in rows:
            if emb_obj.chunk_type == 'metadata' and emb_obj.scheme_id not in metadata_map:
                metadata_map[emb_obj.scheme_id] = (emb_obj, scheme_name, scheme_state)

        for item in sorted_rrf:
            rrf_score, score, emb_obj, scheme_name, scheme_state = item
            sid = emb_obj.scheme_id
            if sid not in seen_schemes:
                seen_schemes.add(sid)
                # If metadata chunk exists for this scheme, use metadata chunk for clean response context
                if sid in metadata_map:
                    m_emb, m_name, m_state = metadata_map[sid]
                    top_items.append((rrf_score, score, m_emb, m_name, m_state))
                else:
                    top_items.append(item)
            if len(top_items) >= top_k:
                break

        retrieved_chunks = []
        context_passages = []

        for rrf_score, score, emb_obj, scheme_name, scheme_state in top_items:
            retrieved_chunks.append(RAGChunkResponse(
                scheme_id=emb_obj.scheme_id,
                scheme_name=scheme_name,
                state=scheme_state,
                chunk_type=emb_obj.chunk_type,
                chunk_text=emb_obj.chunk_text,
                score=round(score, 4)
            ))
            context_passages.append(f"• {scheme_name} ({scheme_state}): {emb_obj.chunk_text[:250]}...")

        context_str = "\n".join(context_passages)

        groq_api_key = os.environ.get("FASTAPI_GROK_API_KEY") or os.environ.get("GROQ_API_KEY") or ""
        groq_model = os.environ.get("FASTAPI_GROK_MODEL")
        llm_answer = ""

        if not retrieved_chunks:
            return RAGSearchResponse(
                query=user_query,
                answer="No relevant health schemes matched your search criteria with sufficient confidence.",
                retrieved_chunks=[]
            )

        if groq_api_key:
            try:
                client = groq.Groq(api_key=groq_api_key)
                prompt = f"""You are ArogyaMitra, an empathetic rural healthcare AI facilitator.
The user asked: "{user_query}"

We retrieved the following candidate health schemes:
{context_str}

INSTRUCTIONS:
1. Give a warm, empathetic 1-2 sentence greeting acknowledging their situation.
2. Briefly present the candidate schemes in bullet points without declaring any single scheme as the absolute top or perfect match.
3. Keep your total response under 100-120 words.
4. Invite the user to ask follow-up questions (e.g. "Would you like to know the eligibility criteria, application process, or required documents for any of these?").
5. End your response exactly with this sentence: "Please select a scheme below for full details."
"""
                response = client.chat.completions.create(
                    model=groq_model,
                    messages=[
                        {"role": "system", "content": "You are ArogyaMitra, a concise healthcare AI facilitator. Provide brief neutral overviews and invite follow-up questions."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=220
                )
                llm_answer = response.choices[0].message.content.strip()
            except Exception as e:
                llm_answer = f"I found {len(retrieved_chunks)} relevant health schemes for your query. Please tap any scheme card below or ask me about eligibility and application steps!"
        else:
            llm_answer = f"I found {len(retrieved_chunks)} relevant health schemes for your query. Please tap any scheme card below or ask me about eligibility and application steps!"

        return RAGSearchResponse(
            query=user_query,
            answer=llm_answer,
            retrieved_chunks=retrieved_chunks
        )
