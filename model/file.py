from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from database import db
import uuid


class File(db.Model):
    __table_name__ = "file"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mime: Mapped[str] = mapped_column(db.String, nullable=False)
    path: Mapped[str] = mapped_column(db.String, nullable=False)
    file_name: Mapped[str] = mapped_column(db.String, nullable=False)
    region: Mapped[str] = mapped_column(db.String, nullable=False)
    size_bytes: Mapped[str] = mapped_column(db.Integer, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, default=False)
    inserted_at: Mapped[str] = mapped_column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[str] = mapped_column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            c.key: getattr(self, c.key) for c in db.inspect(self).mapper.column_attrs
        }
