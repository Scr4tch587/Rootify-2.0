from app.pipeline.influence_rules import extract_influence_candidates
from app.services.evidence_sections import get_evidence_sections
from app.pipeline.claims_store import replace_claims_for_artist
from app.pipeline.scoring.heuristic import HeuristicScorer
from app.pipeline.wikidata_fetch import fetch_wikidata_qid, fetch_wikidata_influences
from app.pipeline.scoring.ml_scorer.wikipedia_scorer.two_stage_wikipedia_scorer import ml_score_wikipedia
from app.pipeline.candidates import extract_candidates
from app.models import Artist
from app.pipeline.mlvalidator import make_input_text
import re

_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")
_WS_RE = re.compile(r"\s+")


def _normalize_name(name: str | None) -> str:
    if not name:
        return ""
    norm = name.lower()
    norm = _NON_ALNUM_RE.sub(" ", norm)
    norm = _WS_RE.sub(" ", norm).strip()
    return norm

async def extract_and_store_wikipedia_claims(db, artist_id):
    artist = await db.get(Artist, artist_id)
    if not artist:
        raise ValueError(f"Artist with id {artist_id} not found")
    artist_name = artist.name

    sections = await get_evidence_sections(artist_id=artist_id, source="wikipedia", db=db)

    candidates = []
    artist_name_norm = _normalize_name(artist_name)
    for sec in sections:
        raw_candidates = await extract_candidates(db, sec.text)
        for raw_candidate in raw_candidates:
            if _normalize_name(raw_candidate.influence_artist) == artist_name_norm:
                continue
            candidate = {
                "influence_artist": raw_candidate.influence_artist,
                "pattern_type": raw_candidate.candidate_method,
                "section_path": sec.section_path,
                "snippet": raw_candidate.snippet,
            }
            candidates.append(candidate)
    
    ml_input = []
    for candidate in candidates:
        ml_input.append(make_input_text(artist_name, candidate["influence_artist"], candidate["snippet"]))
    if ml_input:
        ml_scores = ml_score_wikipedia(ml_input)
        if len(ml_scores) != len(candidates):
            raise RuntimeError("ml_score_wikipedia returned wrong number of scores")
        for candidate, prob_dict in zip(candidates, ml_scores):
            candidate["claim_probability"] = prob_dict.get("p_valid", 0.0)

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
    artist_name_norm = _normalize_name(artist_name)
    for pair in wikidata_pairs:
        if _normalize_name(pair["influencer_label"]) == artist_name_norm:
            continue
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
    artist = await db.get(Artist, artist_id)
    artist_name_norm = _normalize_name(artist.name if artist else "")
    for sec in sections:
        raw_candidates = extract_influence_candidates(sec.text, sec.section_path)
        for candidate in raw_candidates:
            if _normalize_name(candidate.get("influence_artist")) == artist_name_norm:
                continue
            candidates.append(candidate)
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
