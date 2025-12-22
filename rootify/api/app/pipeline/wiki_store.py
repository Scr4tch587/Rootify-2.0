from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import EvidenceSection
from app.pipeline.wiki_sections import extract_relevant_sections

async def store_wikipedia_sections(
        session: AsyncSession,
        artist_id: int,
        artist_name: str,
) -> int:
    sections = extract_relevant_sections(artist_name)

    await session.execute(
        delete(EvidenceSection).where((EvidenceSection.artist_id == artist_id) & (EvidenceSection.source == "wikipedia"))
    )

    rows = []
    for section in sections:
        if not section["text"].strip():
            continue
        evidence_section = EvidenceSection(
            artist_id=artist_id,
            source="wikipedia",
            keyword=section['keyword'],
            section_path=section['section_path'],
            text=section['text'],
            is_fallback=("FALLBACK_FULL_PAGE" == section['keyword']),
        )
        rows.append(evidence_section)
    session.add_all(rows)
    await session.commit()
    return len(sections)    