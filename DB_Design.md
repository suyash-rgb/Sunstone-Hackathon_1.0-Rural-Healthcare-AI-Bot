# Database Design & Data Dictionary - ArogyaMitra Healthcare System

This document defines the relational, spatial, and hybrid-search database design for the **ArogyaMitra Healthcare System**, deployed on **PostgreSQL** with the **pgvector** extension.

---

## 1. System Architecture Diagram

`mermaid
graph TD
    A1[Excel Dataset: health_schemes.xlsx] -->|Seed & Embedding Script| B[(PostgreSQL Database)]
    A2[CSV Dataset: 192,905 Public Health Facilities] -->|Facility Seed Script| B

    subgraph PostgreSQL Relational & Vector Schema
        B1[health_schemes Table - 504 Rows] ---|1-to-Many FK| B2[health_scheme_faqs Table - 5,848 Rows]
        B1 ---|1-to-Many FK| B3[health_scheme_references Table - 1,310 Rows]
        B1 ---|1-to-Many FK| B4[health_scheme_documents Table - 2,714 Rows]
        B1 ---|1-to-Many FK| B5[health_scheme_embeddings Table - Vector + FTS]
        
        B6[healthcare_facilities Table - 192,905 Government Facilities]
    end

    B1 & B2 & B3 & B4 -->|SQL queries| C1[Guided UI REST API]
    B6 -->|Spatial Haversine & Tier Queries| C3[Government Healthcare Facility API]
    
    UserQuery[User Chat Question] --> Engine[Hybrid Search Engine]
    B5 -->|FTS tsvector Search| Engine
    B5 -->|pgvector HNSW Search| Engine
    Engine -->|Rank Fusion Top Chunks| Groq[Groq LLM API]
    Groq -->|Final Response| C2[RAG Chatbot API]
`

---

## 2. Data Dictionary

### Table 1: health_schemes (Core Metadata)
Stores primary scheme details, eligibility, benefits, and administrative categorization.

| Field Name | Data Type | Nullable | Key / Index | Description |
| :--- | :--- | :--- | :--- | :--- |
| id | INTEGER | No | Primary Key | Internal Auto-increment Primary Key |
| scheme_id | VARCHAR(100) | Yes | Unique Index | Unique myScheme portal ID (e.g., SCH-1234) |
| slug | VARCHAR(255) | No | Unique Index | Unique URL-friendly slug for fast lookup |
| scheme_name | VARCHAR(500) | No | B-Tree Index | Full official name of the health scheme |
| short_title | VARCHAR(255) | Yes | None | Abbreviated name or title |
| state | VARCHAR(100) | No | B-Tree Index | Target State/UT name or 'Pan India' |
| department | VARCHAR(255) | Yes | B-Tree Index | Nodal ministry or department |
| level | VARCHAR(50) | No | B-Tree Index | Administrative level ('Central', 'State', 'State/ UT') |
| categories | TEXT | Yes | None | Comma-separated main categories |
| subcategories | TEXT | Yes | None | Comma-separated subcategories |
| tags | TEXT | Yes | None | Keywords and search tags |
| beneficiaries | TEXT | Yes | None | Beneficiary groups (e.g. 'Family, Individual') |
| brief_description | TEXT | Yes | None | Concise 1-2 sentence overview |
| description | TEXT | Yes | None | Comprehensive scheme description |
| benefits | TEXT | Yes | None | Detailed financial/medical coverage details |
| eligibility | TEXT | Yes | None | Detailed age, income, gender, and category criteria |
| application_process | TEXT | Yes | None | Step-by-step application procedure |
| created_at | TIMESTAMP | No | None | System record creation timestamp (utcnow) |
| updated_at | TIMESTAMP | No | None | System record update timestamp (utcnow) |

---

### Table 2: health_scheme_faqs (Normalized FAQs)
Stores granular individual Question-Answer pairs linked to each health scheme.

| Field Name | Data Type | Nullable | Key / Index | Description |
| :--- | :--- | :--- | :--- | :--- |
| id | INTEGER | No | Primary Key | Internal FAQ Auto-increment ID |
| scheme_id | INTEGER | No | Foreign Key (Index) | FK to health_schemes.id (ON DELETE CASCADE) |
| question_number | INTEGER | No | None | Sequential Q&A index number (1, 2, 3...) |
| question | TEXT | No | B-Tree Index | FAQ Question text |
| answer | TEXT | No | None | FAQ Answer text |

---

### Table 3: health_scheme_references (Official Links & Guidelines)
Stores external links, portals, and official guidelines associated with each scheme.

| Field Name | Data Type | Nullable | Key / Index | Description |
| :--- | :--- | :--- | :--- | :--- |
| id | INTEGER | No | Primary Key | Internal Reference Auto-increment ID |
| scheme_id | INTEGER | No | Foreign Key (Index) | FK to health_schemes.id (ON DELETE CASCADE) |
| title | VARCHAR(255) | Yes | None | Display title (e.g. 'Guidelines', 'Official Portal') |
| url | TEXT | No | None | Destination HTTP/HTTPS URL |

---

### Table 4: health_scheme_documents (Required Documents Checklist)
Stores individual required verification documents for applicants.

| Field Name | Data Type | Nullable | Key / Index | Description |
| :--- | :--- | :--- | :--- | :--- |
| id | INTEGER | No | Primary Key | Internal Document Auto-increment ID |
| scheme_id | INTEGER | No | Foreign Key (Index) | FK to health_schemes.id (ON DELETE CASCADE) |
| document_name | TEXT | No | None | Required document description (e.g. 'Aadhaar Card') |

---

### Table 5: health_scheme_embeddings (Hybrid Search Vector Store)
Stores text passages alongside Full-Text Search tokens and pgvector dense vector embeddings.

| Field Name | Data Type | Nullable | Key / Index | Description |
| :--- | :--- | :--- | :--- | :--- |
| id | INTEGER | No | Primary Key | Internal Chunk Auto-increment ID |
| scheme_id | INTEGER | No | Foreign Key (Index) | FK to health_schemes.id (ON DELETE CASCADE) |
| chunk_type | VARCHAR(50) | No | B-Tree Index | Chunk type ('metadata', 'faq', 'eligibility', 'benefits') |
| chunk_text | TEXT | No | None | Raw text passage used as LLM context |
| fts_tokens | TSVECTOR | No | GIN Index | PostgreSQL Full-Text Search Tokens |
| embedding | VECTOR(384) | No | HNSW Index | 384-dim Dense Vector |
| created_at | TIMESTAMP | No | None | Embedding indexing timestamp |

---

### Table 6: healthcare_facilities (Government Public Infrastructure)
Stores 192,905 verified public healthcare facilities (Sub-Centres, PHCs, CHCs, SDHs, DHs, Medical Colleges) sourced from NIN/Government databases for rural & emergency health routing.

| Field Name | Data Type | Nullable | Key / Index | Description |
| :--- | :--- | :--- | :--- | :--- |
| id | INTEGER | No | Primary Key | Auto-increment Primary Key |
| sr_no | INTEGER | Yes | B-Tree Index | Source serial number from NIN dataset |
| facility_name | VARCHAR(500) | No | B-Tree Index | Name of government health facility |
| address | TEXT | Yes | None | Full address description |
| street | TEXT | Yes | None | Street / Village detail |
| landmark | TEXT | Yes | None | Nearby landmark |
| locality | TEXT | Yes | None | Locality name |
| pincode | VARCHAR(20) | Yes | B-Tree Index | 6-digit postal code |
| landline_number | VARCHAR(100) | Yes | None | Official landline / contact number |
| latitude | FLOAT | Yes | B-Tree Index | Geolocation Latitude |
| longitude | FLOAT | Yes | B-Tree Index | Geolocation Longitude |
| facility_type | VARCHAR(100) | No | B-Tree Index | Type ('Sub-Centre', 'PHC', 'CHC', 'District Hospital', etc.) |
| tier_level | VARCHAR(50) | No | B-Tree Index | Tier level ('Tier 1 (Primary)', 'Tier 2 (Secondary)', 'Tier 3 (Tertiary)') |
| state_name | VARCHAR(100) | No | B-Tree Index | State / Union Territory name |
| district_name | VARCHAR(100) | No | B-Tree Index | District name |
| taluka_name | VARCHAR(100) | Yes | B-Tree Index | Taluka name |
| block_name | VARCHAR(100) | Yes | B-Tree Index | Block name |
| created_at | TIMESTAMP | No | None | Record creation timestamp |
| updated_at | TIMESTAMP | No | None | Record last update timestamp |

---

## 3. Database Indexes

1. **idx_health_schemes_state_level**: Composite B-Tree index on (state, level) for high-speed Guided UI filtering.
2. **idx_health_schemes_slug**: Unique index on slug for single scheme detail API queries.
3. **idx_scheme_faqs_scheme_id**: Foreign Key B-Tree index for fetching scheme Q&As.
4. **idx_scheme_embeddings_fts**: GIN index on ts_tokens for sub-millisecond keyword full-text search.
5. **idx_scheme_embeddings_vec**: HNSW index on embedding using Cosine Distance (ector_cosine_ops) for fast semantic similarity search.
6. **idx_facility_state_district**: Composite B-Tree index on (state_name, district_name) for high-speed location filtering of 192k facilities.
7. **idx_facility_lat_lon**: Composite B-Tree index on (latitude, longitude) for spatial bounding-box & distance calculation.
8. **idx_facility_tier_state**: Composite B-Tree index on (tier_level, state_name) for primary/secondary healthcare tier routing.
