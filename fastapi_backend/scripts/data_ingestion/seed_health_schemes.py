import sys
import os
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

import time
import re
import ast
import asyncio
import pandas as pd
from sqlalchemy import text
from fastembed import TextEmbedding

from app.db.session import engine, AsyncSessionLocal
from app.db.base import Base
from app.db.models.health_scheme import (
    HealthScheme, HealthSchemeFAQ, HealthSchemeReference,
    HealthSchemeDocument, HealthSchemeEmbedding
)

DATASET_PATH = os.path.join(backend_dir, "datasets", "health_schemes.xlsx")

import html

def clean_val(val):
    if pd.isna(val) or val is None:
        return None
    s = str(val).strip()
    if not s or s.lower() == 'nan':
        return None
    
    # 1. Replace <br> tags and <p> boundaries with newlines to preserve spacing
    s = re.sub(r'<br\s*/?>', '\n', s, flags=re.IGNORECASE)
    s = re.sub(r'</?p\s*>', '\n', s, flags=re.IGNORECASE)
    
    # 2. Strip all remaining HTML tags (like <b>, <i>, <a>, <span>)
    s = re.sub(r'<[^>]+>', '', s)
    
    # 3. Unescape HTML entities (&amp; -> &, &quot; -> ", etc.)
    s = html.unescape(s)
    
    # 4. Remove strange unicode replacements (like object replacement character)
    s = s.replace('\ufffc', '')
    
    # 5. Normalize whitespace while preserving essential newlines and tabs
    s = re.sub(r'\n{3,}', '\n\n', s) # collapse 3+ newlines to 2
    
    return s.strip()

def parse_faqs(raw):
    if not raw:
        return []
    text_val = str(raw).strip()
    pairs = re.findall(r'Q:\s*(.*?)\s*\n\s*A:\s*(.*?)(?=\n\s*Q:|$)', text_val, re.DOTALL)
    return [(q.strip(), a.strip()) for q, a in pairs if q.strip() and a.strip()]

def parse_references(raw):
    if not raw:
        return []
    text_val = str(raw).strip()
    matches = re.findall(r'([A-Za-z0-9\s_\-\(\)]+):\s*(https?://[^\s]+)', text_val)
    return [(t.strip(), u.strip()) for t, u in matches if u.strip()]

def parse_documents(raw):
    if not raw:
        return []
    s = str(raw).strip()
    if s.startswith('[') and s.endswith(']'):
        try:
            lst = ast.literal_eval(s)
            return [str(item).strip() for item in lst if str(item).strip()]
        except Exception:
            pass
    items = re.split(r'\n?\d+\.\s*', s)
    return [i.strip() for i in items if i.strip()]

async def seed_database():
    start_time = time.time()
    print("--- 1. Initializing PostgreSQL Database Schema ---", flush=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("\n--- 2. Loading Dataset from Excel ---", flush=True)
    df = pd.read_excel(DATASET_PATH)
    print(f"Loaded {len(df)} schemes from Excel.", flush=True)

    print("\n--- 3. Initializing FastEmbed Model ---", flush=True)
    embed_model = TextEmbedding()

    print("\n--- 4. Preparing Objects and Text Chunks ---", flush=True)
    schemes_to_insert = []
    faqs_to_insert = []
    refs_to_insert = []
    docs_to_insert = []
    embedding_payloads = []

    for idx, row in df.iterrows():
        scheme_name = clean_val(row.get('SchemeName'))
        if not scheme_name:
            continue

        slug_val = clean_val(row.get('Slug')) or f"scheme-{idx+1}"
        
        scheme = HealthScheme(
            scheme_id=clean_val(row.get('SchemeId')),
            slug=slug_val,
            scheme_name=scheme_name,
            short_title=clean_val(row.get('ShortTitle')),
            state=clean_val(row.get('State')) or "Pan India",
            department=clean_val(row.get('Department')),
            level=clean_val(row.get('Level')) or "Central",
            categories=clean_val(row.get('Categories')),
            subcategories=clean_val(row.get('Subcategories')),
            tags=clean_val(row.get('Tags')),
            beneficiaries=clean_val(row.get('Beneficiaries')),
            brief_description=clean_val(row.get('BriefDescription')),
            description=clean_val(row.get('Description')),
            benefits=clean_val(row.get('Benefits')),
            eligibility=clean_val(row.get('Eligibility')),
            application_process=clean_val(row.get('ApplicationProcess'))
        )
        schemes_to_insert.append(scheme)

        # FAQs
        raw_faqs = parse_faqs(clean_val(row.get('Faqs')))
        for q_idx, (q, a) in enumerate(raw_faqs, start=1):
            faqs_to_insert.append((slug_val, q_idx, q, a))
            faq_chunk_text = f"Scheme: {scheme_name} | State: {scheme.state}\nQuestion: {q}\nAnswer: {a}"
            embedding_payloads.append(("faq", faq_chunk_text, slug_val))

        # References
        raw_refs = parse_references(clean_val(row.get('References')))
        for r_title, r_url in raw_refs:
            refs_to_insert.append((slug_val, r_title, r_url))

        # Documents
        raw_docs = parse_documents(clean_val(row.get('Documents')))
        for doc_name in raw_docs:
            docs_to_insert.append((slug_val, doc_name))

        # Summary Chunk
        summary_parts = [f"Scheme: {scheme_name} ({scheme.state})"]
        if scheme.brief_description:
            summary_parts.append(f"Description: {scheme.brief_description}")
        if scheme.benefits:
            summary_parts.append(f"Benefits: {scheme.benefits[:300]}")
        if scheme.eligibility:
            summary_parts.append(f"Eligibility: {scheme.eligibility[:300]}")
        
        summary_text = "\n".join(summary_parts)
        embedding_payloads.append(("metadata", summary_text, slug_val))

    print(f"Parsed {len(schemes_to_insert)} schemes, {len(faqs_to_insert)} FAQs, {len(embedding_payloads)} total embedding chunks.", flush=True)

    print("\n--- 5. Batch Embeddings Generation (batch_size=32) ---", flush=True)
    t_emb_start = time.time()
    texts_only = [p[1] for p in embedding_payloads]
    # batch_size=32 prevents ONNX memory bad allocation error
    vectors_list = list(embed_model.embed(texts_only, batch_size=32))
    print(f"Generated {len(vectors_list)} vector embeddings in {time.time() - t_emb_start:.2f} seconds!", flush=True)

    print("\n--- 6. Ingesting into PostgreSQL ---", flush=True)
    async with AsyncSessionLocal() as session:
        await session.execute(text("TRUNCATE TABLE health_schemes RESTART IDENTITY CASCADE;"))
        await session.commit()

        # Insert Schemes
        session.add_all(schemes_to_insert)
        await session.flush()

        slug_to_id = {s.slug: s.id for s in schemes_to_insert}

        # Insert FAQs
        faq_objs = [
            HealthSchemeFAQ(scheme_id=slug_to_id[slug], question_number=q_idx, question=q, answer=a)
            for slug, q_idx, q, a in faqs_to_insert
        ]
        session.add_all(faq_objs)

        # Insert References
        ref_objs = [
            HealthSchemeReference(scheme_id=slug_to_id[slug], title=title, url=url)
            for slug, title, url in refs_to_insert
        ]
        session.add_all(ref_objs)

        # Insert Documents
        doc_objs = [
            HealthSchemeDocument(scheme_id=slug_to_id[slug], document_name=doc_name)
            for slug, doc_name in docs_to_insert
        ]
        session.add_all(doc_objs)

        # Insert Embeddings
        emb_objs = [
            HealthSchemeEmbedding(
                scheme_id=slug_to_id[payload[2]],
                chunk_type=payload[0],
                chunk_text=payload[1],
                embedding=vec.tolist()
            )
            for payload, vec in zip(embedding_payloads, vectors_list)
        ]
        session.add_all(emb_objs)

        # Commit everything in ONE atomic transaction at the very end
        await session.commit()

    total_duration = time.time() - start_time
    print(f"\n=== SEEDING COMPLETE IN {total_duration:.2f} SECONDS ===")
    print(f"Total Schemes Inserted: {len(schemes_to_insert)}")
    print(f"Total FAQs Inserted: {len(faq_objs)}")
    print(f"Total References Inserted: {len(ref_objs)}")
    print(f"Total Documents Inserted: {len(doc_objs)}")
    print(f"Total Embeddings Inserted: {len(emb_objs)}", flush=True)

if __name__ == "__main__":
    asyncio.run(seed_database())
