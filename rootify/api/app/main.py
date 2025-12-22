from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.schemas import ArtistCreate, ArtistOut
from app.models import Artist
from app.services.artists import create_artist, list_artists
from app.pipeline.wiki_store import store_wikipedia_sections

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