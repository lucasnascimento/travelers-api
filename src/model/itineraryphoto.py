import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.file import File


from database import db


class Photo(db.Model):
    __tablename__ = "itinerary_photo"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    position: Mapped[int] = mapped_column(db.Integer, nullable=False)
    title: Mapped[str] = mapped_column(db.String, nullable=False)
    description: Mapped[str] = mapped_column(db.String, nullable=False)
    photo_id: Mapped[Optional[str]] = mapped_column(ForeignKey("file.id"))
    photo: Mapped[Optional[File]] = relationship("File", uselist=False)

    itinerary_id: Mapped[Optional[str]] = mapped_column(ForeignKey("itinerary.id"))

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
        if hasattr(self, "photo") and self.photo is not None:
            result["photo"] = self.photo.to_dict()
        return result
