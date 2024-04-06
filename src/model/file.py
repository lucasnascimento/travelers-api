from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from config import ENVIRONMENT
from upload import get_path, upload_file

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

    def get_path(self):
        return get_path(self.region, self.path)

    def to_dict(self):
        path = self.get_path()

        return {
            "id": str(self.id),
            "path": path,
            "file_name": self.file_name,
            "mime": self.mime,
            "size_bytes": self.size_bytes,
        }
