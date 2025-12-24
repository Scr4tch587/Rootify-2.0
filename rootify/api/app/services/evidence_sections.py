from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import EvidenceSection

async def get_evidence_sections(
        db: AsyncSession,
        artist_id: int,
        source: str | None = None,
):
    stmt = select(EvidenceSection).where(
        EvidenceSection.artist_id == artist_id
    )

    if source:
        stmt = stmt.where(EvidenceSection.source == source)

    result = await db.execute(stmt)
    return result.scalars().all()