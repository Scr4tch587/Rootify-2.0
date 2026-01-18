import re 
import spacy

from app.services.musicbrainz import fetch_mbid_cached, fetch_deduped_name_cached

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple
from app.models import ArtistNameVariant
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

_nlp = spacy.load("en_core_web_sm")  

@dataclass(frozen=True)
class NameVariantEntry:
    canonical_name: str
    variant_norm: str
    tokens_norm: Tuple[str, ...]
    token_count: int
    char_len: int
    source: str
    match_form: str

@dataclass(frozen=True)
class ExtractedCandidate:
    influence_artist: str
    mention_text: str
    snippet: str
    candidate_method: str
    match_form: str
    mbid: str

_seed_index_cache: Dict[str, List[NameVariantEntry]] | None = None
_seed_index_built_at: datetime | None = None
_seed_index_ttl = timedelta(minutes=1440)

def normalize_text(name: str) -> str:
    _NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")
    _WS_RE = re.compile(r"\s+")
    name = name.lower()
    name = _NON_ALNUM_RE.sub(" ", name)
    name = _WS_RE.sub(" ", name).strip()
    return name


def _is_cache_fresh(now: datetime) -> bool:
    if _seed_index_cache is None or _seed_index_built_at is None:
        return False
    return (now - _seed_index_built_at) < _seed_index_ttl

async def load_artist_name_variants(session: AsyncSession, force_rebuild: bool = False) -> dict[str, list[NameVariantEntry]]:
    global _seed_index_cache, _seed_index_built_at

    now = datetime.now(timezone.utc)
    if not force_rebuild and _is_cache_fresh(now):
        return _seed_index_cache  
    
    stmt = select(
        ArtistNameVariant.canonical_name,
        ArtistNameVariant.variant_norm,
        ArtistNameVariant.first_token,
        ArtistNameVariant.token_count,
        ArtistNameVariant.char_len,
        ArtistNameVariant.source,
        ArtistNameVariant.match_form,
    )

    rows = (await session.execute(stmt)).all()
    index: Dict[str, List[NameVariantEntry]] = {}
    for canonical_name, variant_norm, first_token, token_count, char_len, source, match_form in rows:
        if not variant_norm:
            continue
        tokens = tuple(variant_norm.split())
        if not tokens:
            continue

        ft = (first_token or tokens[0]).strip()
        if not ft:
            continue

        entry = NameVariantEntry(
            canonical_name=canonical_name,
            variant_norm=variant_norm,
            tokens_norm=tokens,
            token_count=token_count if token_count else len(tokens),
            char_len=char_len if char_len else len(variant_norm),
            source=source,
            match_form=match_form,
        )

        index.setdefault(ft, []).append(entry)
    
    for ft, bucket in index.items():
        index[ft] = sorted(bucket, key=lambda e: (e.token_count, e.char_len), reverse=True)
    _seed_index_cache = index       
    _seed_index_built_at = now

    return _seed_index_cache

async def extract_candidates(
    session: AsyncSession,
    text: str,
    include_ner: bool = False,
) -> List[ExtractedCandidate]:
    # STRING MATCH
    seeded_artist_variants = await load_artist_name_variants(session)
    doc = normalize_text(text)
    doc_tokens = doc.split()
    num_tokens = len(doc_tokens)
    out = []
    for i in range(num_tokens):
        bucket = seeded_artist_variants.get(doc_tokens[i])
        if not bucket: continue

        for entry in bucket:
            k = entry.token_count
            j = i + k
            if j > num_tokens: continue
            if tuple(doc_tokens[i:j]) == entry.tokens_norm:
                out.append(
                    ExtractedCandidate(
                        influence_artist=entry.canonical_name,
                        mention_text=" ".join(doc_tokens[i:j]),
                        snippet=text,
                        candidate_method="string_match",
                        match_form=entry.match_form,
                        mbid=None,
                    )
                )
                break

    # NER
    if include_ner:
        ner_doc = _nlp(text)
        for ent in ner_doc.ents:
            if ent.label_ not in  {"PERSON", "ORG"}:
                continue
            norm_ent = normalize_text(ent.text)
            out.append(ExtractedCandidate(
                influence_artist = None,
                mention_text=ent.text,
                snippet=text,
                candidate_method="ner",
                match_form=None,
                mbid=None,
            ))

    #deduping
    filtered_out = []
    seen = set()
    for candidate in out:
        if candidate.candidate_method == "ner":
            mbid = await fetch_mbid_cached(candidate.mention_text)
        else:
            mbid = await fetch_mbid_cached(candidate.influence_artist)
        if mbid:
            if ("mbid", mbid) not in seen:
                seen.add(("mbid", mbid))
                new_candidate = ExtractedCandidate(
                    influence_artist = await fetch_deduped_name_cached(mbid),
                    mbid = mbid,
                    mention_text = candidate.mention_text,
                    snippet = candidate.snippet,
                    candidate_method = candidate.candidate_method,
                    match_form = candidate.match_form,
                )   

                filtered_out.append(new_candidate)
        else:
            if candidate.candidate_method != "ner":
                if not candidate.influence_artist.strip(): continue
                key = normalize_text(candidate.influence_artist)
            else:
                continue
            if ("name", key) not in seen:
                seen.add(("name", key))
                filtered_out.append(candidate)
    return filtered_out
