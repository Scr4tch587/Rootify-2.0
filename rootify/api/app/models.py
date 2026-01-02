from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Integer, Text, func
from datetime import datetime
import sqlalchemy as sa

class Base(DeclarativeBase):
    pass

class Artist(Base):
    __tablename__ = "artists"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    evidence_claims = relationship(
        "EvidenceClaim",
        back_populates="artist",
    
    )

class EvidenceSection(Base):
    __tablename__ = "evidence_sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    artist_id: Mapped[int] = mapped_column(ForeignKey("artists.id", ondelete="CASCADE"), nullable=False)

    source: Mapped[str] = mapped_column(Text, nullable=False)
    keyword: Mapped[str] = mapped_column(Text, nullable=False)
    section_path: Mapped[str] = mapped_column(Text, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    is_fallback: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

class EvidenceClaim(Base):
    __tablename__ = "evidence_claims"

    id: Mapped[int] = mapped_column(primary_key=True)
     
    artist_id: Mapped[int] = mapped_column(
        ForeignKey("artists.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    source: Mapped[str] = mapped_column(nullable=False)
    influence_artist: Mapped[str] = mapped_column(index=True, nullable=False)
    pattern_type: Mapped[str] = mapped_column(nullable=False)

    section_path: Mapped[str] = mapped_column(nullable=False)
    snippet: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=sa.text("now()"),
        nullable=False,
    )

    artist: Mapped["Artist"] = relationship(back_populates="evidence_claims")
    extraction_version: Mapped[str] = mapped_column(nullable=False)
    claim_probability: Mapped[float] = mapped_column(nullable=False, default=1.0)

class ArtistNameVariant(Base):
    __tablename__ = "artist_name_variants"
    __table_args__ = (
        sa.UniqueConstraint(
            "variant_norm",
            "canonical_name",
            name="uq_artist_name_variants_variant_norm_canonical_name",
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
     
    canonical_name: Mapped[str] = mapped_column(nullable=False)
    variant_name: Mapped[str] = mapped_column(nullable=False)
    variant_norm: Mapped[str] = mapped_column(index=True, nullable=False)
    first_token: Mapped[str] = mapped_column(index=True, nullable=False)
    token_count: Mapped[int] = mapped_column(nullable=False)
    char_len: Mapped[int] = mapped_column(nullable=False)
    source: Mapped[str] = mapped_column(nullable=False)
    match_form: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=sa.text("now()"),
        nullable=False,
    )

# class InfluenceCandidate(Base):
#     __tablename__ = "influence_candidates"
#     artist_id: Mapped[int] = mapped_column(
#         ForeignKey("artists.id", ondelete="CASCADE"),
#         index=True,
#         nullable=False,
#     )
#     mbid: Mapped[str] = mapped_column(index=True, nullable=True)
#     source: Mapped[str] = mapped_column(nullable=False)
#     influence_artist: Mapped[str] = mapped_column(index=True, nullable=False)
#     section_path: Mapped[str] = mapped_column(nullable=False)
#     snippet: Mapped[str] = mapped_column(Text, nullable=False)
#     mention_text: Mapped[str] = mapped_column(Text, nullable=False)
#     candidate_method: Mapped[str] = mapped_column(nullable=False)
#     match_form: Mapped[str] = mapped_column(nullable=True)