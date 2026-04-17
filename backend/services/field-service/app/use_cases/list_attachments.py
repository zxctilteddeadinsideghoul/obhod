from app.repositories import AttachmentsRepository
from app.schemas import AttachmentRead


class ListAttachmentsUseCase:
    def __init__(self, attachments_repository: AttachmentsRepository) -> None:
        self.attachments_repository = attachments_repository

    async def execute(
        self,
        entity_type: str,
        entity_id: str,
        author_id: str,
        user_role: str,
    ) -> list[AttachmentRead]:
        attachments = await self.attachments_repository.list_for_entity(entity_type, entity_id, author_id, user_role)
        return [
            AttachmentRead(
                id=item.id,
                entity_type=item.entity_type,
                entity_id=item.entity_id,
                file_name=item.file_name,
                mime_type=item.mime_type,
                size_bytes=item.size_bytes,
                checksum=item.checksum,
                storage_uri=item.storage_uri,
                download_url=f"/api/field/attachments/{item.id}/download",
                payload_json=item.payload_json,
            )
            for item in attachments
        ]
