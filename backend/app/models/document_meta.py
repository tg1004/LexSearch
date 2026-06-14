from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    court: Mapped[str | None] = mapped_column(String(200), nullable=True)
    date: Mapped[date | None] = mapped_column(Date, nullable=True)
    case_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    outcome: Mapped[str | None] = mapped_column(String(100), nullable=True)
    judges: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    full_text_length: Mapped[int | None] = mapped_column(Integer, nullable=True)
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    indexed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    bookmarks = relationship("Bookmark", back_populates="document")
