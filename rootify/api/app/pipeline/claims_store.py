from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.constants import CURRENT_EXTRACTION_VERSION

from app.models import EvidenceClaim

async def replace_claims_for_artist(db: AsyncSession, artist_id: int, source: str, claims: list[dict]):
    await db.execute(
        delete(EvidenceClaim).where(
            (EvidenceClaim.artist_id == artist_id) &
            (EvidenceClaim.source == source)
        )
    )

    db.add_all(
        [
            EvidenceClaim(
                artist_id=artist_id,
                source=source,
                influence_artist=c["influence_artist"],
                pattern_type=c["pattern_type"],
                section_path=c["section_path"],
                snippet=c["snippet"],   
                extraction_version=CURRENT_EXTRACTION_VERSION,
            )
            for c in claims
        ]
    )

    await db.commit()