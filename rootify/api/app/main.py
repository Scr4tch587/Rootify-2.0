from app.services.seed_variants import seed_artist_variants_index
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
from app.services.dataset_generator import generate_dataset_for_artist
from app.services.influences import get_influences

# TEST ONLY
from app.pipeline.youtube_candidates import extract_youtube_candidates

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/admin/seed_artist_index")
async def seed_artist_index(db: AsyncSession = Depends(get_db)):
    return await seed_artist_variants_index(db)

@app.post("/artists/", response_model=ArtistOut)
async def post_artist(payload: ArtistCreate, db: AsyncSession = Depends(get_db)):
    return await create_artist(db, payload.name)

@app.post("/artists/bulk", response_model=list[int])
async def post_artists_bulk(payload: list[ArtistCreate], db: AsyncSession = Depends(get_db)):
    """Create or return existing artists for a list of artist payloads and return their ids."""
    ids: list[int] = []
    for artist in payload:
        created = await create_artist(db, artist.name)
        ids.append(created.id)
    return ids

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

@app.get("/generate_dataset/")
async def generate_dataset(
    db: AsyncSession = Depends(get_db),
):  
    TIER_1_ARTIST_IDS = [
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15
    ]

    TIER_2_ARTIST_IDS = [
        16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30
    ]

    TIER_3_ARTIST_IDS = [
        31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43
    ]

    TIER_4_ARTIST_IDS = [
        44, 45, 46, 47, 48, 49, 50, 51
    ]

    TIER_5_ARTIST_IDS = [
        52, 53, 54, 55, 56, 57, 58
    ]

    TIER_6_ARTIST_IDS = [
        59, 60, 61, 62, 63, 64, 65, 66, 67, 68
    ]

    TIER_7_ARTIST_IDS = [
        69, 70, 71, 72, 73, 74, 75, 76, 77, 78
    ]

    TIER_8_ARTIST_IDS = [
        79, 80, 81, 82, 83, 84, 85, 86
    ]

    input_texts = []
    for id in TIER_8_ARTIST_IDS:
        input_texts.extend(await generate_dataset_for_artist(db, id))
    return input_texts

# @app.get("/test")
# async def test_endpoint(
#     db: AsyncSession = Depends(get_db),
# ):
#     candidates = await extract_youtube_candidates(db, test_string)
#     return candidates