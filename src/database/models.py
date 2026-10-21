import uuid

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _uuid() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class Xasida(Base):
    __tablename__ = "xasidas"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    og_name: Mapped[str | None] = mapped_column(String)
    aka_name: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[str] = mapped_column(String, default="Cheikh Ahmadou Bamba")
    language: Mapped[str] = mapped_column(String, default="ar")
    pdf_path: Mapped[str | None] = mapped_column(String)
    ar_pdf_path: Mapped[str | None] = mapped_column(String)
    fr_pdf_path: Mapped[str | None] = mapped_column(String)
    an_pdf_path: Mapped[str | None] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text)

    versions: Mapped[list["Version"]] = relationship(back_populates="xasida")


class Reference(Base):
    # "references" is a reserved SQL keyword — using xasida_references
    __tablename__ = "xasida_references"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String, nullable=False)
    year: Mapped[int | None] = mapped_column(Integer)
    url: Mapped[str | None] = mapped_column(String)

    versions: Mapped[list["Version"]] = relationship(back_populates="reference")


class Version(Base):
    __tablename__ = "versions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    xasida_id: Mapped[str] = mapped_column(String, ForeignKey("xasidas.id"), nullable=False)
    reference_id: Mapped[str | None] = mapped_column(String, ForeignKey("xasida_references.id"))
    artist: Mapped[str | None] = mapped_column(String)
    year: Mapped[int | None] = mapped_column(Integer)
    audio_path: Mapped[str] = mapped_column(String, nullable=False)
    duration: Mapped[float | None] = mapped_column(Float)
    source: Mapped[str | None] = mapped_column(String)
    recording_quality: Mapped[str | None] = mapped_column(String)

    xasida: Mapped["Xasida"] = relationship(back_populates="versions")
    reference: Mapped["Reference | None"] = relationship(back_populates="versions")
    segments: Mapped[list["AudioSegment"]] = relationship(back_populates="version")


class AudioSegment(Base):
    __tablename__ = "audio_segments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    version_id: Mapped[str] = mapped_column(String, ForeignKey("versions.id"), nullable=False)
    segment_index: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[float] = mapped_column(Float, nullable=False)
    end_time: Mapped[float] = mapped_column(Float, nullable=False)
    embedding_model: Mapped[str] = mapped_column(String, nullable=False)
    embedding_version: Mapped[str] = mapped_column(String, nullable=False)

    version: Mapped["Version"] = relationship(back_populates="segments")
