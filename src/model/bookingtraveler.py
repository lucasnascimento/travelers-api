import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


from database import db


class BookingTraveler(db.Model):
    __tablename__ = "booking_traveler"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    booking_id: Mapped[Optional[str]] = mapped_column(ForeignKey("booking.id"))

    traveler_name: Mapped[str] = mapped_column(db.String, nullable=False)
    traveler_birthdate: Mapped[str] = mapped_column(db.Date, nullable=False)
    traveler_gender: Mapped[str] = mapped_column(db.String, nullable=False)
    traveler_extras: Mapped[str] = mapped_column(db.JSON, nullable=True)
    total_cents: Mapped[int] = mapped_column(
        db.Integer, nullable=False, server_default="0"
    )

    is_deleted: Mapped[bool] = mapped_column(db.Boolean, default=False)
    inserted_at: Mapped[str] = mapped_column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[str] = mapped_column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
