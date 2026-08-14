from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    url: Mapped[str | None] = mapped_column(Text)
    license_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Artist(Base):
    __tablename__ = "artists"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    profile_url: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Tattoo(Base):
    __tablename__ = "tattoos"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    image_url: Mapped[str] = mapped_column(Text)
    image_hash: Mapped[str | None] = mapped_column(String)
    duplicate_of: Mapped[UUID | None] = mapped_column(ForeignKey("tattoos.id"))
    source_id: Mapped[UUID] = mapped_column(ForeignKey("sources.id"))
    artist_id: Mapped[UUID | None] = mapped_column(ForeignKey("artists.id"))
    semantic_description: Mapped[str | None] = mapped_column(Text)
    subject: Mapped[str | None] = mapped_column(Text)
    style: Mapped[str | None] = mapped_column(Text)
    placement: Mapped[str | None] = mapped_column(Text)
    color: Mapped[str | None] = mapped_column(String)
    size: Mapped[str | None] = mapped_column(String)
    complexity: Mapped[str | None] = mapped_column(String)
    orientation: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
