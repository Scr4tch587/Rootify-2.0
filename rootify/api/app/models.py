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

class InfluenceCandidate(Base):
    __tablename__ = "influence_candidates"
    artist_id: Mapped[int] = mapped_column(
        ForeignKey("artists.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    source: Mapped[str] = mapped_column(nullable=False)
    influence_artist_raw: Mapped[str] = mapped_column(index=True, nullable=False)
    section_path: Mapped[str] = mapped_column(nullable=False)
    snippet: Mapped[str] = mapped_column(Text, nullable=False)
    candidate_method: Mapped[str] = mapped_column(nullable=False)
    mention_start: Mapped[int] = mapped_column(nullable=True)
    mention_end: Mapped[int] = mapped_column(nullable=True)