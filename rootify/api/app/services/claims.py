from app.pipeline.influence_rules import extract_influence_candidates
from app.services.evidence_sections import get_evidence_sections
from app.pipeline.claims_store import replace_claims_for_artist

async def extract_and_store_wikipedia_claims(db, artist_id):
    sections = await get_evidence_sections(artist_id=artist_id, source="wikipedia", db=db)

    candidates = []
    for sec in sections:
        candidates.extend(extract_influence_candidates(sec.text, sec.section_path))

    await replace_claims_for_artist(
        db=db,
        artist_id=artist_id,
        source="wikipedia",
        claims=candidates,
    )

    return {
        "artist_id": artist_id,
        "source": "wikipedia",
        "sections_used": len(sections),
        "claims_extracted": len(candidates),
    }