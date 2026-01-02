from app.services.constants import YOUTUBE_ARTIST_SEED, THE_STRIP_DENY 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from app.models import ArtistNameVariant
import re

_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")
_WS_RE = re.compile(r"\s+")

async def seed_artist_variants_index(
    db: AsyncSession,
):  
    await db.execute(delete(ArtistNameVariant).where(ArtistNameVariant.source == "seed"))
    name_variants = []

    for name in YOUTUBE_ARTIST_SEED:
        norm_name = name.lower()
        norm_name = _NON_ALNUM_RE.sub(" ", norm_name)
        norm_name = _WS_RE.sub(" ", norm_name).strip()
        norm_tokens = norm_name.split()
        token_count = len(norm_tokens)
        char_len = len(norm_name)
        if name.lower().startswith("the ") and len(norm_tokens) > 1:
            if norm_name not in THE_STRIP_DENY:
                stripped_norm = " ".join(norm_tokens[1:])
                stripped_tokens = stripped_norm.split()
                name_variants.append(ArtistNameVariant(
                    canonical_name=name,
                    variant_name=name[4:].strip(),
                    variant_norm=stripped_norm,
                    first_token = stripped_tokens[0],
                    token_count = len(stripped_tokens),
                    char_len = len(stripped_norm),
                    source = "seed",
                    match_form = "the_stripped",
                ))
        name_variants.append(ArtistNameVariant(
            canonical_name=name,
            variant_name=name,
            variant_norm=norm_name,
            first_token = norm_tokens[0],
            token_count = token_count,
            char_len = char_len,
            source = "seed",
            match_form = "full",
        ))
    db.add_all(name_variants)
    await db.commit()
    return {"inserted_variants": len(name_variants)}