# Rootify  
**Explainable Artist Influence Graph**

Rootify is an **evidence-first music discovery system** that maps **artist influences** using real textual sources instead of opaque similarity metrics.

Given an artist name, Rootify aims to return:
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

#### Data Model
- Relational schema designed for **evidence-first reasoning**
- Artists stored as canonical nodes
- Evidence stored as **raw, traceable text** (not derived claims)

#### Wikipedia Ingestion Pipeline (Evidence Source #1)
- Dynamic Wikipedia page fetch by artist name
- Section-tree traversal (including nested subsections)
- Keyword-prioritized section selection:
  - Influences  
  - Artistry  
  - Musical style  
  - Songwriting  
  - Themes  
  - Background / Career (fallback)
- Automatic fallback to full-page text when no relevant sections exist
- Empty or container-only sections filtered out
- One database row per meaningful section
- Safe re-ingestion (delete + reinsert per artist/source)
- Fully async ingestion and persistence
- FastAPI endpoint to trigger ingestion on demand

#### API Endpoints
- `GET /health`
- `POST /artists` (idempotent get-or-create)
- `GET /artists`
- `POST /artists/{artist_id}/ingest/wikipedia`

---

### 🚧 In Progress / Planned

#### Evidence → Influence Extraction
- Sentence-level extraction of **explicit artist-to-artist influence claims**
- Rule-based phrase detection (e.g. “influenced by”, “draws inspiration from”)
- Named-entity validation to ensure **artists only** appear as nodes

#### Explainable ML Components
- Sentence-level classifier to score likelihood of influence claims  
- Evidence weighting based on:
  - phrasing strength  
  - source type  
  - repetition across documents  
- Aggregation of evidence into influence edges
- Learning-to-rank model over aggregated edge features

#### Additional Evidence Sources
- Wikidata (structured “influenced by” relations)
- YouTube interview transcripts (first-person statements)
- Reviews / journalism (critical commentary)

#### Read & Query APIs
- Fetch evidence per artist
- Fetch ranked influences with expandable citations
- Support for reproducible results and debugging

#### Frontend (Later Stage)
- React (Vite) frontend
- Ranked influence lists
- Expandable evidence cards
- Source badges and citation links

---

## Core Design Principles (Non-Negotiable)

- **Artists are the only nodes**
- **Edges represent influence, not similarity**
- **No influence without textual evidence**
- **ML assists reasoning, it does not replace it**
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
- (Planned) sentence-level classifiers and ranking models

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
```
