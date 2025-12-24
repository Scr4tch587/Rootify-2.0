from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_db
from app.schemas import ArtistCreate, ArtistOut, EvidenceSectionOut, InfluenceCandidateOut, InfluenceOut
from app.models import Artist, EvidenceClaim
from app.services.artists import create_artist, list_artists
from app.services.evidence_sections import get_evidence_sections
from app.pipeline.claims_store import replace_claims_for_artist
from app.pipeline.wiki_store import store_wikipedia_sections
from app.pipeline.influence_rules import extract_influence_candidates 
from app.pipeline.influence_aggregate import aggregate_influence

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/artists/", response_model=ArtistOut)
async def post_artist(payload: ArtistCreate, db: AsyncSession = Depends(get_db)):
    return await create_artist(db, payload.name)

@app.get("/artists/", response_model=list[ArtistOut])
async def get_artists(db: AsyncSession = Depends(get_db)):
    return await list_artists(db)

@app.post("/artists/{artist_id}/ingest/wikipedia")
async def ingest_wikipedia_sections(artist_id: int, session: AsyncSession = Depends(get_db)):
    artist = await session.get(Artist, artist_id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    num_sections = await store_wikipedia_sections(
        session,
        artist_id,
        artist.name,
    )
    return {"artist_id": artist.id, "source": "wikipedia", "inserted_sections": num_sections}

@app.get("/artists/{artist_id}/evidence", response_model=list[EvidenceSectionOut])
async def read_evidence(
    artist_id: int,
    source: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await get_evidence_sections(
        artist_id=artist_id,
        source=source,
        db=db,
    )

@app.get("/artists/{artist_id}/influence_candidates", response_model=list[InfluenceCandidateOut])
async def influence_candidates(
    artist_id: int,
    source: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    sections = await get_evidence_sections(
        artist_id=artist_id,
        source=source,
        db=db,
    )
    out = []
    for sec in sections:
        candidates = extract_influence_candidates(sec.text, sec.section_path)
        out.extend(candidates)
    return out

@app.get("/artists/{artist_id}/influences", response_model=list[InfluenceOut])
async def read_influences(
    artist_id: int,
    source: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    sections = await get_evidence_sections(
        artist_id=artist_id,
        source=source,
        db=db,
    )
    candidates = []
    for sec in sections:
        cands = extract_influence_candidates(sec.text, sec.section_path)
        candidates.extend(cands)

    return aggregate_influence(candidates)

@app.post("/artists/{artist_id}/extract/wikipedia")
async def extract_wikipedia_claims(
    artist_id: int,
    db: AsyncSession = Depends(get_db),
):
    sections = await get_evidence_sections(artist_id=artist_id, source="wikipedia", db=db)

    candidates = []
    for sec in sections:
        candidates.extend(extract_influence_candidates(sec.text, sec.section_path))

        await replace_claims_for_artist(
            db=db,
            artist_id=artist_id,
            source="wikipedia",
            claims=candidates,
        )

        return {
            "artist_id": artist_id,
            "source": "wikipedia",
            "sections_used": len(sections),
            "claims_extracted": len(candidates),
        }