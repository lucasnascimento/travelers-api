import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from database import db


class Booking(db.Model):
    __tablename__ = "booking"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    itinerary_id: Mapped[Optional[str]] = mapped_column(ForeignKey("itinerary.id"))

    payer_name: Mapped[str] = mapped_column(db.String, nullable=False)
    payer_email: Mapped[str] = mapped_column(db.String, nullable=False)
    payer_phone: Mapped[str] = mapped_column(db.String, nullable=False)
    payer_document: Mapped[str] = mapped_column(db.String, nullable=False)

    is_deleted: Mapped[bool] = mapped_column(db.Boolean, default=False)
    inserted_at: Mapped[str] = mapped_column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[str] = mapped_column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
