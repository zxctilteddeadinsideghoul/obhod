import hashlib

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import AttachmentsRepository
from app.schemas import AttachmentRead
from app.services import ObjectStorage


class UploadAttachmentUseCase:
    def __init__(
        self,
        session: AsyncSession,
        attachments_repository: AttachmentsRepository,
        object_storage: ObjectStorage,
    ) -> None:
        self.session = session
        self.attachments_repository = attachments_repository
        self.object_storage = object_storage

    async def execute(
        self,
        entity_type: str,
        entity_id: str,
        file: UploadFile,
        payload_json: dict,
        author_id: str,
        user_role: str,
    ) -> AttachmentRead:
        await self.attachments_repository.ensure_access(entity_type, entity_id, author_id, user_role)

        content = await file.read()
        if not content:
            raise ValueError("File is empty")

        file_name = file.filename or "attachment.bin"
        mime_type = file.content_type or "application/octet-stream"
        checksum = hashlib.sha256(content).hexdigest()
        storage_uri = self.object_storage.upload(file_name, mime_type, content)

        attachment = await self.attachments_repository.create(
            entity_type=entity_type,
            entity_id=entity_id,
            file_name=file_name,
            mime_type=mime_type,
            size_bytes=len(content),
            checksum=checksum,
            storage_uri=storage_uri,
            payload_json=payload_json,
            author_id=author_id,
            user_role=user_role,
        )
        await self.session.commit()
        return self._to_read(attachment)

    def _to_read(self, attachment) -> AttachmentRead:
        return AttachmentRead(
            id=attachment.id,
            entity_type=attachment.entity_type,
            entity_id=attachment.entity_id,
            file_name=attachment.file_name,
            mime_type=attachment.mime_type,
            size_bytes=attachment.size_bytes,
            checksum=attachment.checksum,
            storage_uri=attachment.storage_uri,
            download_url=f"/api/field/attachments/{attachment.id}/download",
            payload_json=attachment.payload_json,
        )
