import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.file import File
from model.institution import Institution

from database import db


class Itinerary(db.Model):
    __tablename__ = "itinerary"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    status: Mapped[str] = mapped_column(db.String, nullable=False, default="draft")
    current_step: Mapped[str] = mapped_column(
        db.String, nullable=False, default="general"
    )
    title: Mapped[str] = mapped_column(db.String, nullable=False)
    boarding_date: Mapped[str] = mapped_column(db.Date, nullable=False)
    landing_date: Mapped[str] = mapped_column(db.Date, nullable=False)
    seats: Mapped[int] = mapped_column(db.Integer, nullable=False)
    seat_price: Mapped[float] = mapped_column(db.Numeric, nullable=False)
    purchase_deadline: Mapped[str] = mapped_column(db.Date, nullable=False)
    installments: Mapped[str] = mapped_column(db.Integer, nullable=False)
    details: Mapped[str] = mapped_column(db.String, nullable=False)
    summary: Mapped[str] = mapped_column(db.String, nullable=False)
    services: Mapped[str] = mapped_column(db.String, nullable=False)
    terms_and_conditions: Mapped[str] = mapped_column(db.String, nullable=False)
    institution_id: Mapped[Optional[str]] = mapped_column(ForeignKey("institution.id"))
    cover_id: Mapped[Optional[str]] = mapped_column(ForeignKey("file.id"))

    institution: Mapped[Optional[Institution]] = relationship(
        "Institution", uselist=False
    )
    cover: Mapped[Optional[File]] = relationship("File", uselist=False)

    is_deleted: Mapped[bool] = mapped_column(db.Boolean, default=False)
    inserted_at: Mapped[str] = mapped_column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[str] = mapped_column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        result = {
            c.key: getattr(self, c.key) for c in db.inspect(self).mapper.column_attrs
        }
        if hasattr(self, "cover") and self.cover is not None:
            result["cover"] = self.cover.to_dict()
        if hasattr(self, "institution") and self.institution is not None:
            result["institution"] = self.institution.to_dict()
        return result
