from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models import Artist

async def create_artist(db, name: str) -> Artist:
    result = await db.execute(select(Artist).where(Artist.name == name))
    existing = result.scalar_one_or_none()
    if existing is not None:
        return existing

    artist = Artist(name=name)
    db.add(artist)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        result = await db.execute(select(Artist).where(Artist.name == name))
        return result.scalar_one()

    await db.refresh(artist)
    return artist

async def list_artists(db: AsyncSession) -> list[Artist]:
    result = await db.execute(select(Artist).order_by(Artist.id))
    return list(result.scalars().all())