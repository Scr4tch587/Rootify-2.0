from sqlalchemy import select, func
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Artist, EvidenceSection, EvidenceClaim
from app.pipeline.wiki_store import store_wikipedia_sections
from app.services.constants import CURRENT_EXTRACTION_VERSION
from app.services.claims import extract_and_store_wikipedia_claims
from app.services.claims import extract_and_store_wikidata_claims
from app.services.claims import extract_and_store_youtube_claims
from app.pipeline.influence_aggregate import aggregate_influence
from app.services.cache_client import cache_get_json, cache_put_json
from app.services.lambda_client import invoke_artifact_writer
import datetime

def check_cache_update_requirements(evidence_last_updated: datetime, claims_version_stored: str, TTL: datetime.timedelta) -> dict[str, bool]:
    needs_ingest = False
    needs_extract = False    

    if not evidence_last_updated:
        needs_ingest = True
        needs_extract = True
        return {"needs_ingest": needs_ingest, "needs_extract": needs_extract}
    if not claims_version_stored:
        needs_extract = True
    if (datetime.datetime.now(datetime.timezone.utc) - evidence_last_updated > TTL):
        needs_ingest = True
        needs_extract = True
        return {"needs_ingest": needs_ingest, "needs_extract": needs_extract}
    if (claims_version_stored != CURRENT_EXTRACTION_VERSION):
        needs_extract = True
    return {"needs_ingest": needs_ingest, "needs_extract": needs_extract}

async def get_influences(
        db: AsyncSession,
        artist_id: int,
        source: str | None = None,
):
    source = source or "wikipedia"

    cache_key = (
        f"rootify:v1:influences:artist_id={artist_id}:source={source}"
        f":rules={CURRENT_EXTRACTION_VERSION}"
    )
    cached = await cache_get_json(cache_key)
    if cached is not None:
        return cached

    stmt = select(EvidenceClaim.extraction_version).where(EvidenceClaim.artist_id == artist_id).where(EvidenceClaim.source == source).limit(1)
    claims_version_stored = (await db.execute(stmt)).scalar_one_or_none()

    stmt = select(func.max(EvidenceSection.created_at)).where(EvidenceSection.artist_id == artist_id).where(EvidenceSection.source == source)
    evidence_last_updated = (await db.execute(stmt)).scalar_one_or_none()

    if source == "wikipedia":
        TTL = datetime.timedelta(days=1)
    elif source == "wikidata":
        TTL = datetime.timedelta(days=7)
    elif source == "youtube":
        TTL = datetime.timedelta(days=7)

    status_dict = check_cache_update_requirements(evidence_last_updated, claims_version_stored, TTL=TTL)

    artist = await db.get(Artist, artist_id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    artist_name = artist.name

    if status_dict["needs_ingest"]:
        await store_wikipedia_sections(db, artist_id, artist.name)

    if status_dict["needs_extract"]:
        if source == "wikipedia":
            await extract_and_store_wikipedia_claims(db, artist_id)
        if source == "wikidata":
            await extract_and_store_wikidata_claims(db, artist_id)
        if source == "youtube":
            await extract_and_store_youtube_claims(db, artist_id)

    candidates = []
    stmt = (
        select(EvidenceClaim)
        .where(EvidenceClaim.artist_id == artist_id)
        .where(EvidenceClaim.source == source)
    )
    result = await db.execute(stmt)
    claims = result.scalars().all()

    for claim in claims:
        candidates.append({
            "artist_name": artist_name,
            "influence_artist": claim.influence_artist,
            "snippet": claim.snippet,
            "section_path": claim.section_path,
            "pattern_type": claim.pattern_type,
            "claim_probability": claim.claim_probability,
        })

    out = aggregate_influence(candidates)

    await cache_put_json(cache_key, out, ttl_seconds=3600)

    payload = {
        "artist_id": artist_id,
        "artist_name": artist_name,
        "source": source,
        "rules_version": CURRENT_EXTRACTION_VERSION,
        "computed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "influences": out,
    }
    await invoke_artifact_writer(payload)

    return out

