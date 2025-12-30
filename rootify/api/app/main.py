from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.schemas import ArtistCreate, ArtistOut, EvidenceSectionOut, InfluenceCandidateOut, InfluenceOut
from app.models import Artist
from app.services.artists import create_artist, list_artists
from app.services.evidence_sections import get_evidence_sections
from app.pipeline.wiki_store import store_wikipedia_sections
from app.pipeline.youtube_store import store_youtube_sections
from app.pipeline.influence_rules import extract_influence_candidates 
from app.services.claims import extract_and_store_wikipedia_claims
from app.services.claims import extract_and_store_wikidata_claims
from app.services.claims import extract_and_store_youtube_claims
from app.services.influences import get_influences

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

@app.post("/artists/{artist_id}/ingest/youtube/{video_id}")
async def ingest_youtube_sections(artist_id: int, video_id: str, session: AsyncSession = Depends(get_db)):
    artist = await session.get(Artist, artist_id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    num_sections = await store_youtube_sections(
        session,
        artist_id,
        video_id,
    )
    return {"artist_id": artist.id, "source": "youtube", "inserted_sections": num_sections}

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
    return await get_influences(
        db=db, 
        artist_id=artist_id,
        source=source,
    )

@app.post("/artists/{artist_id}/extract/wikipedia")
async def extract_wikipedia_claims(
    artist_id: int,
    db: AsyncSession = Depends(get_db),
):  
    return await extract_and_store_wikipedia_claims(db, artist_id)  

@app.post("/artists/{artist_id}/extract/wikidata")
async def extract_wikidata_claims(
    artist_id: int,
    db: AsyncSession = Depends(get_db),
):  
    return await extract_and_store_wikidata_claims(db, artist_id)  

@app.post("/artists/{artist_id}/extract/youtube")
async def extract_youtube_claims(
    artist_id: int,
    db: AsyncSession = Depends(get_db),
):  
    return await extract_and_store_youtube_claims(db, artist_id)  