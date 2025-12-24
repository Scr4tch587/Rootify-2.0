# Rootify  
**Explainable Artist Influence Graph**

Rootify is an **evidence-first music discovery system** that maps **artist influences** using real textual sources instead of opaque similarity metrics.

Given an artist name, Rootify returns:
- a ranked list of influencing artists  
- concrete **textual evidence** supporting each influence  
- **citations** pointing to where each claim came from  

The core principle is **explainability**: every influence must be traceable back to real text.

---

## Why Rootify?

Most music discovery tools rely on:
- collaborative filtering  
- embedding similarity  
- black-box recommendation models  

Rootify instead asks a different question:

> *“What artists explicitly influenced this artist, and where is that stated?”*

This makes Rootify:
- auditable  
- interpretable  
- useful for learning about music history, not just discovering similar sounds  

---

## Project Status

### ✅ Implemented (Current)

#### Backend & Infrastructure
- Dockerized **FastAPI + PostgreSQL** stack using Docker Compose  
- Async SQLAlchemy sessions with proper dependency injection  
- Alembic migrations for schema versioning  
- Idempotent artist creation (safe re-creation without duplicates)  

#### Evidence-First Data Model
- **Artists** as canonical nodes  
- **Evidence sections** stored as raw, traceable text (Wikipedia sections)
- **Evidence claims** stored separately as *derived artifacts*
- Clear separation between:
  - *source evidence* (immutable text)
  - *derived claims* (recomputable outputs)

This enables reproducibility, auditability, and safe re-extraction.

#### Wikipedia Ingestion Pipeline (Evidence Source #1)
- Dynamic Wikipedia page fetch by artist name  
- Full section-tree traversal (including nested subsections)  
- Keyword-prioritized section selection:
  - Influences  
  - Artistry  
  - Musical style  
  - Songwriting  
  - Themes  
  - Background / Career (fallback)  
- Automatic fallback to full-page text if no relevant sections exist  
- Empty or container-only sections filtered out  
- One database row per meaningful section  
- **Safe re-ingestion** (delete + reinsert per artist/source)  
- Fully async ingestion and persistence  

#### Evidence → Claim Extraction
- Rule-based extraction of **explicit influence statements**
- Pattern-based detection (e.g. “influenced by”, “draws inspiration from”)
- Claims stored with:
  - influence artist
  - snippet
  - section path
  - pattern type
  - extraction version
- Deduplication via unique constraint across semantic claim fields  

#### Cache Invalidation & Versioning (Major Milestone)
- **Two-layer cache model**:
  - Evidence freshness (time-based TTL)
  - Claim freshness (extraction-version based)
- Deterministic cache decision logic:
  - Re-ingest evidence if stale or missing
  - Re-extract claims if logic version changes
- O(1) staleness checks using:
  - max(evidence.created_at)
  - stored extraction_version
- Guarantees:
  - No stale claims
  - No unnecessary recomputation
  - Safe evolution of extraction logic

#### Service-Layer Orchestration
- Clear separation between:
  - HTTP endpoints
  - cache policy
  - ingestion pipelines
  - extraction pipelines
- Services decide *what* to refresh
- Pipelines focus on *how* to compute
- Endpoints remain thin and declarative

---

### API Endpoints

#### Core
- `GET /health`
- `POST /artists` (idempotent get-or-create)
- `GET /artists`

#### Ingestion & Extraction
- `POST /artists/{artist_id}/ingest/wikipedia`
- `POST /artists/{artist_id}/extract/wikipedia`

#### Read APIs
- `GET /artists/{artist_id}/influences`
  - Automatically:
    - checks cache freshness
    - re-ingests evidence if needed
    - re-extracts claims if needed
    - returns ranked, explainable influence results

---

## Core Design Principles (Non-Negotiable)

- **Artists are the only nodes**
- **Edges represent influence, not similarity**
- **No influence without textual evidence**
- **Derived data is always recomputable**
- **Cache invalidation is explicit and deterministic**
- **All outputs must be explainable in an interview**

---

## Tech Stack

**Backend**
- Python
- FastAPI
- Async SQLAlchemy
- Alembic

**Data & NLP**
- spaCy
- pandas
- Rule-based extraction (current)
- ML-assisted ranking (planned)

**Database**
- PostgreSQL

**Infrastructure**
- Docker
- Docker Compose

**Frontend (Planned)**
- React (Vite)
- Tailwind CSS
- shadcn/ui

---

## Running Locally

```bash
# start services
docker compose up -d

# stop services
docker compose down
