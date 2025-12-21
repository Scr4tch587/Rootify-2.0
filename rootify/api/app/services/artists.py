from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Artist

async def create_artist(db: AsyncSession, name: str) -> Artist:
    artist = Artist(name = name)
    db.add(artist)
    await db.commit()
    await db.refresh(artist)
    return artist

async def list_artists(db: AsyncSession) -> list[Artist]:
    result = await db.execute(select(Artist).order_by(Artist.id))
    return list(result.scalars().all())