import mimetypes
import os
import uuid
from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.utils import secure_filename

from database import db
from upload import get_path, upload_file

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

    @classmethod
    def create_and_upload(cls, file, environment):
        # hack to add webp mimetype
        if not mimetypes.guess_type('example.webp')[0]:
            mimetypes.add_type('image/webp', '.webp')

        new_uuid = uuid.uuid4()
        filename = secure_filename(f"{new_uuid}__{file.filename}")
        mime_type = mimetypes.guess_type(filename)[0]
        file.seek(0, os.SEEK_END)
        size_bytes = file.tell()
        file.seek(0)
        path = upload_file(file, filename)
        new_file = cls(
            id=new_uuid,
            mime=mime_type,
            path=path,
            file_name=filename,
            region=environment,
            size_bytes=size_bytes,
        )
        db.session.add(new_file)
        db.session.flush()
        return new_file

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
