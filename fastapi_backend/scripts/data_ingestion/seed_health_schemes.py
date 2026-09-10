import sys
import os
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

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

def clean_val(val):
    if pd.isna(val) or val is None:
        return None
    s = str(val).strip()
    return s if s and s.lower() != 'nan' else None

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
    print("--- 1. Initializing PostgreSQL Database Schema ---", flush=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("\n--- 2. Loading Dataset from Excel ---", flush=True)
    df = pd.read_excel(DATASET_PATH)
    print(f"Loaded {len(df)} schemes from Excel.", flush=True)

    print("\n--- 3. Initializing FastEmbed Model ---", flush=True)
    embed_model = TextEmbedding()

    print("\n--- 4. Seeding Data into PostgreSQL ---", flush=True)
    async with AsyncSessionLocal() as session:
        await session.execute(text("TRUNCATE TABLE health_schemes RESTART IDENTITY CASCADE;"))
        await session.commit()
        print("Truncated health_schemes table for fresh seed.", flush=True)

        total_schemes = 0
        total_faqs = 0
        total_refs = 0
        total_docs = 0
        total_embeddings = 0

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
            session.add(scheme)
            await session.flush()
            total_schemes += 1

            # 1. FAQs
            raw_faqs = parse_faqs(clean_val(row.get('Faqs')))
            for q_idx, (q, a) in enumerate(raw_faqs, start=1):
                faq_obj = HealthSchemeFAQ(
                    scheme_id=scheme.id,
                    question_number=q_idx,
                    question=q,
                    answer=a
                )
                session.add(faq_obj)
                total_faqs += 1

                faq_chunk_text = f"Scheme: {scheme.scheme_name} | State: {scheme.state}\nQuestion: {q}\nAnswer: {a}"
                faq_vec = list(embed_model.embed([faq_chunk_text]))[0].tolist()
                emb_obj = HealthSchemeEmbedding(
                    scheme_id=scheme.id,
                    chunk_type="faq",
                    chunk_text=faq_chunk_text,
                    embedding=faq_vec
                )
                session.add(emb_obj)
                total_embeddings += 1

            # 2. References
            raw_refs = parse_references(clean_val(row.get('References')))
            for r_title, r_url in raw_refs:
                ref_obj = HealthSchemeReference(
                    scheme_id=scheme.id,
                    title=r_title,
                    url=r_url
                )
                session.add(ref_obj)
                total_refs += 1

            # 3. Documents
            raw_docs = parse_documents(clean_val(row.get('Documents')))
            for doc_name in raw_docs:
                doc_obj = HealthSchemeDocument(
                    scheme_id=scheme.id,
                    document_name=doc_name
                )
                session.add(doc_obj)
                total_docs += 1

            # 4. Summary Chunk
            summary_parts = [f"Scheme: {scheme.scheme_name} ({scheme.state})"]
            if scheme.brief_description:
                summary_parts.append(f"Description: {scheme.brief_description}")
            if scheme.benefits:
                summary_parts.append(f"Benefits: {scheme.benefits[:300]}")
            if scheme.eligibility:
                summary_parts.append(f"Eligibility: {scheme.eligibility[:300]}")
            
            summary_text = "\n".join(summary_parts)
            summary_vec = list(embed_model.embed([summary_text]))[0].tolist()
            summary_emb = HealthSchemeEmbedding(
                scheme_id=scheme.id,
                chunk_type="metadata",
                chunk_text=summary_text,
                embedding=summary_vec
            )
            session.add(summary_emb)
            total_embeddings += 1

            if total_schemes % 25 == 0:
                await session.commit()
                print(f"Seeded & committed {total_schemes}/{len(df)} schemes...", flush=True)

        await session.commit()
        print(f"\n=== SEEDING COMPLETE ===")
        print(f"Total Schemes Inserted: {total_schemes}")
        print(f"Total FAQs Inserted: {total_faqs}")
        print(f"Total References Inserted: {total_refs}")
        print(f"Total Documents Inserted: {total_docs}")
        print(f"Total Vector Embeddings Generated: {total_embeddings}", flush=True)

if __name__ == "__main__":
    asyncio.run(seed_database())
