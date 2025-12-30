from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import EvidenceSection
from app.pipeline.youtube_sections import fetch_youtube_sections

async def store_youtube_sections(
        session: AsyncSession,
        artist_id: int,
        video_id: str,
) -> int:
    sections = fetch_youtube_sections(video_id)

    await session.execute(
        delete(EvidenceSection).where((EvidenceSection.artist_id == artist_id) & (EvidenceSection.source == "youtube"))
    )

    rows = []
    for section in sections:
        if not section["text"].strip():
            continue
        evidence_section = EvidenceSection(
            artist_id=artist_id,
            source="youtube",
            keyword=section['keyword'],
            section_path=section['section_path'],
            text=section['text'],
            is_fallback=False,
        )
        rows.append(evidence_section)
    session.add_all(rows)
    await session.commit()
    return len(sections)    