from app.repositories import AttachmentsRepository
from app.services import ObjectStorage


class DownloadAttachmentUseCase:
    def __init__(
        self,
        attachments_repository: AttachmentsRepository,
        object_storage: ObjectStorage,
    ) -> None:
        self.attachments_repository = attachments_repository
        self.object_storage = object_storage

    async def execute(self, attachment_id: str, author_id: str, user_role: str) -> tuple[bytes, str, str]:
        attachment = await self.attachments_repository.get(attachment_id, author_id, user_role)
        content = self.object_storage.download(attachment.storage_uri)
        return content, attachment.file_name, attachment.mime_type
