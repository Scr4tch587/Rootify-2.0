from app.pipeline.influence_rules import extract_influence_candidates
from app.services.evidence_sections import get_evidence_sections
from app.pipeline.wiki_store import store_wikipedia_sections
from app.models import Artist
from app.pipeline.mlvalidator import make_input_text
from fastapi import HTTPException

async def generate_dataset_for_artist(db, artist_id):
    artist = await db.get(Artist, artist_id)
    artist_name = artist.name
    await store_wikipedia_sections(db, artist_id, artist_name)
    sections = await get_evidence_sections(artist_id=artist_id, source="wikipedia", db=db)

    candidates = []
    for sec in sections:
        candidates.extend(extract_influence_candidates(sec.text, sec.section_path, artist_name))

    input_texts = []
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    for candidate in candidates:
        input_texts.append(make_input_text(artist_name, candidate["influence_artist"], candidate["snippet"]))
    return input_texts