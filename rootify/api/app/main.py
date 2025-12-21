from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.schemas import ArtistCreate, ArtistOut
from app.services.artists import create_artist, list_artists

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