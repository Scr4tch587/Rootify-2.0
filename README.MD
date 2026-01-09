# Rootify  
**Explainable Artist Influence Graph**

Rootify is an **evidence-first music discovery system** that maps **artist influence relationships** using real textual sources rather than similarity metrics or black-box recommendations.

Given an artist, Rootify returns:
- a ranked list of **influencing artists**
- **verbatim evidence snippets** supporting each claim
- **citations** pointing to the original source

If an influence cannot be supported by text, Rootify does not assert it.

---

## Motivation

Most music discovery systems focus on answering:
> “Which artists sound similar?”

Rootify instead addresses:
> **“Which artists explicitly influenced this artist, and where is that stated?”**

This framing prioritizes:
- interpretability
- auditability
- usefulness for understanding music history rather than surface-level similarity

---

## System Overview

Rootify operates as a **multi-stage, evidence-preserving pipeline**:

```
Wikipedia / Wikidata / YouTube  
↓  
Normalized documents  
↓  
Candidate artist extraction  
↓  
ML validation and direction resolution  
↓  
Evidence-backed influence claims  
↓  
Ranked, explainable output
```

Each stage is explicit and independently inspectable.

---

## Evidence Sources

- **Wikipedia** — encyclopedic, third-person influence statements  
- **Wikidata** — structured “influenced by” relations with high precision  
- **YouTube** — interviews and first-person influence statements  

All sources are normalized into a common representation before downstream processing.

---

## Evidence-First Design

Rootify does not construct abstract graph edges directly.

Instead, it stores **sentence-level evidence claims**, each annotated with:
- source reference (page, section, or timestamp)
- verbatim text snippet
- influence strength category
- ML-derived confidence score

Influence strength is computed by **aggregating evidence**, not by counting mentions.

---

## Machine Learning (Explainable by Design)

Machine learning is used to **support** influence reasoning, not replace it.
- Binary classifier filters non-influence sentences and assigns confidence  
- Probabilistic outputs directly inform scoring and ranking decisions  
- No generative steps are used, and no influence is created without evidence.

---

## Tech Stack (WIP)

- **Backend:** FastAPI, async SQLAlchemy, Alembic  
- **Database:** PostgreSQL (claims-first relational schema)  
- **NLP / ML:** spaCy, Sentence Transformers, Logistic Regression  
- **Infrastructure:** Docker, Docker Compose  

---

## Why Rootify Is Distinct

- Evidence-first graph construction  
- Explicit, explainable ML components  
- Multi-source validation  
- Clear separation between extraction, validation, and ranking  
- Designed to be defensible in technical interviews  

---

## Project Status

- Wikipedia + Wikidata pipelines: ✅ stable  
- YouTube ingestion and candidate extraction: ✅ stable  
- Two-stage ML validation: ✅ trained and evaluated  
- Architecture: ✅ locked  
- Frontend: ⏭️ planned  

