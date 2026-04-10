from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import EvidenceSection
from app.pipeline.youtube_discovery import discover_youtube_videos
from app.pipeline.youtube_store import store_youtube_sections


async def ingest_youtube_for_artist(
    db: AsyncSession,
    artist_id: int,
    artist_name: str,
    max_results: int = 5,
) -> int:
    video_ids = await discover_youtube_videos(artist_name, max_results=max_results)
    if not video_ids:
        return 0

    await db.execute(
        delete(EvidenceSection).where(
            (EvidenceSection.artist_id == artist_id)
            & (EvidenceSection.source == "youtube")
        )
    )
    await db.commit()

    total_sections = 0
    for video_id in video_ids:
        try:
            total_sections += await store_youtube_sections(db, artist_id, video_id)
        except Exception:
            continue

    return total_sections
