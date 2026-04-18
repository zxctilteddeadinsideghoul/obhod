from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Attachment, AuditLog, ChecklistInstance, ChecklistItemResult, Defect, Equipment, JournalEntry, RoundInstance


SUPPORTED_ENTITY_TYPES = {"checklist_item_result", "checklist_result", "equipment", "defect", "round"}


class AttachmentsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        entity_type: str,
        entity_id: str,
        file_name: str,
        mime_type: str,
        size_bytes: int,
        checksum: str,
        storage_uri: str,
        payload_json: dict,
        author_id: str,
        user_role: str,
    ) -> Attachment:
        entity_type = self.normalize_entity_type(entity_type)
        await self.ensure_access(entity_type, entity_id, author_id, user_role)
        attachment = Attachment(
            id=str(uuid4()),
            entity_type=entity_type,
            entity_id=entity_id,
            file_name=file_name,
            mime_type=mime_type,
            size_bytes=size_bytes,
            checksum=checksum,
            storage_uri=storage_uri,
            payload_json=payload_json,
        )
        self.session.add(attachment)

        now = datetime.now(timezone.utc)
        self.session.add(
            JournalEntry(
                id=str(uuid4()),
                event_ts=now,
                event_type="attachment.created",
                entity_type="attachment",
                entity_id=attachment.id,
                employee_id=author_id,
                payload_json={
                    "authorId": author_id,
                    "targetEntityType": entity_type,
                    "targetEntityId": entity_id,
                    "fileName": file_name,
                    "mimeType": mime_type,
                    "sizeBytes": size_bytes,
                },
            )
        )
        self.session.add(
            AuditLog(
                id=str(uuid4()),
                entity_type="attachment",
                entity_id=attachment.id,
                op="create",
                author_id=author_id,
                before_json=None,
                after_json={
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "file_name": file_name,
                    "mime_type": mime_type,
                    "size_bytes": size_bytes,
                    "storage_uri": storage_uri,
                },
            )
        )
        await self.session.flush()
        return attachment

    async def list_for_entity(
        self,
        entity_type: str,
        entity_id: str,
        author_id: str,
        user_role: str,
    ) -> list[Attachment]:
        entity_type = self.normalize_entity_type(entity_type)
        await self.ensure_access(entity_type, entity_id, author_id, user_role)
        result = await self.session.execute(
            select(Attachment)
            .where(
                Attachment.entity_type == entity_type,
                Attachment.entity_id == entity_id,
            )
            .order_by(Attachment.created_at.desc())
        )
        return list(result.scalars().all())

    async def get(self, attachment_id: str, author_id: str, user_role: str) -> Attachment:
        attachment = await self.session.get(Attachment, attachment_id)
        if attachment is None:
            raise KeyError(f"Attachment {attachment_id} not found")
        await self.ensure_access(attachment.entity_type, attachment.entity_id, author_id, user_role)
        return attachment

    async def ensure_access(self, entity_type: str, entity_id: str, author_id: str, user_role: str) -> None:
        entity_type = self.normalize_entity_type(entity_type)
        if entity_type not in SUPPORTED_ENTITY_TYPES:
            raise ValueError(f"Unsupported attachment entity type: {entity_type}")

        if user_role == "ADMIN":
            await self._ensure_entity_exists(entity_type, entity_id)
            return

        if entity_type == "round":
            round_instance = await self.session.get(RoundInstance, entity_id)
            if round_instance is None:
                raise KeyError(f"Round {entity_id} not found")
            if round_instance.employee_id != author_id:
                raise PermissionError("Round is not assigned to current worker")
            return

        if entity_type == "checklist_item_result":
            result = await self._get_checklist_item_result(entity_id)
            if result.checklist_instance.round_instance.employee_id != author_id:
                raise PermissionError("Checklist result is not assigned to current worker")
            return

        raise PermissionError("Only admin can attach files to this entity type")

    def normalize_entity_type(self, entity_type: str) -> str:
        aliases = {
            "checklist_result": "checklist_item_result",
        }
        return aliases.get(entity_type, entity_type)

    async def _ensure_entity_exists(self, entity_type: str, entity_id: str) -> None:
        model_by_type = {
            "equipment": Equipment,
            "defect": Defect,
            "round": RoundInstance,
        }
        if entity_type == "checklist_item_result":
            await self._get_checklist_item_result(entity_id)
            return

        model = model_by_type[entity_type]
        if await self.session.get(model, entity_id) is None:
            raise KeyError(f"{entity_type} {entity_id} not found")

    async def _get_checklist_item_result(self, entity_id: str) -> ChecklistItemResult:
        result = await self.session.execute(
            select(ChecklistItemResult)
            .join(ChecklistInstance, ChecklistInstance.id == ChecklistItemResult.checklist_instance_id)
            .join(RoundInstance, RoundInstance.id == ChecklistInstance.round_instance_id)
            .where(ChecklistItemResult.id == entity_id)
        )
        checklist_result = result.scalars().one_or_none()
        if checklist_result is None:
            raise KeyError(f"Checklist item result {entity_id} not found")
        await self.session.refresh(checklist_result, attribute_names=["checklist_instance"])
        await self.session.refresh(checklist_result.checklist_instance, attribute_names=["round_instance"])
        return checklist_result
