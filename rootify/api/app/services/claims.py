from app.pipeline.influence_rules import extract_influence_candidates
from app.services.evidence_sections import get_evidence_sections
from app.pipeline.claims_store import replace_claims_for_artist
from app.pipeline.scoring.heuristic import HeuristicScorer
from app.pipeline.wikidata_fetch import fetch_wikidata_qid, fetch_wikidata_influences
from app.models import Artist

async def extract_and_store_wikipedia_claims(db, artist_id):
    sections = await get_evidence_sections(artist_id=artist_id, source="wikipedia", db=db)

    candidates = []
    for sec in sections:
        candidates.extend(extract_influence_candidates(sec.text, sec.section_path))
    scorer = HeuristicScorer()

    heuristic_scores = scorer.score_batch(candidates)
    if len(heuristic_scores) != len(candidates):
        raise RuntimeError("HeuristicScorer returned wrong number of scores")
    for candidate, prob in zip(candidates, heuristic_scores):
        candidate["claim_probability"] = prob

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

async def extract_and_store_wikidata_claims(db, artist_id):
    artist = await db.get(Artist, artist_id)
    if not artist:
        raise ValueError(f"Artist with id {artist_id} not found")
    artist_name = artist.name

    qid = await fetch_wikidata_qid(artist_name)
    wikidata_pairs = await fetch_wikidata_influences(qid["qid"])
    candidates = []
    for pair in wikidata_pairs:
        candidate = {
            "influence_artist": pair["influencer_label"],
            "pattern_type": "direct",
            "section_path": "wikidata:P737",
            "snippet": "Wikidata: influenced by (P737)",
            "claim_probability": 1.0,
        }
        candidates.append(candidate)
    await replace_claims_for_artist(
        db=db,
        artist_id=artist_id,
        source="wikidata",
        claims=candidates,
    )

    return {
        "artist_id": artist_id,
        "source": "wikidata",
        "claims_extracted": len(candidates),
    }

async def extract_and_store_youtube_claims(db, artist_id):
    sections = await get_evidence_sections(artist_id=artist_id, source="youtube", db=db)

    candidates = []
    for sec in sections:
        candidates.extend(extract_influence_candidates(sec.text, sec.section_path))
    scorer = HeuristicScorer()

    heuristic_scores = scorer.score_batch(candidates)
    if len(heuristic_scores) != len(candidates):
        raise RuntimeError("HeuristicScorer returned wrong number of scores")
    for candidate, prob in zip(candidates, heuristic_scores):
        candidate["claim_probability"] = prob

    await replace_claims_for_artist(
        db=db,
        artist_id=artist_id,
        source="youtube",
        claims=candidates,
    )

    return {
        "artist_id": artist_id,
        "source": "youtube",
        "sections_used": len(sections),
        "claims_extracted": len(candidates),
    }

