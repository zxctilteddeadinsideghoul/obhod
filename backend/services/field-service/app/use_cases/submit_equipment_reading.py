from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import EquipmentRepository
from app.schemas import (
    EquipmentParameterReadingCreate,
    EquipmentParameterReadingRead,
    EquipmentParameterReadingSubmitRead,
)


class SubmitEquipmentReadingUseCase:
    def __init__(
        self,
        session: AsyncSession,
        equipment_repository: EquipmentRepository,
    ) -> None:
        self.session = session
        self.equipment_repository = equipment_repository

    async def execute(
        self,
        equipment_id: str,
        payload: EquipmentParameterReadingCreate,
        user_id: str,
    ) -> EquipmentParameterReadingSubmitRead:
        equipment = await self.equipment_repository.get(equipment_id)
        parameter_def = await self.equipment_repository.get_parameter_def(payload.parameter_def_id)
        reading, status, message = await self.equipment_repository.create_reading(
            equipment,
            parameter_def,
            payload,
            user_id,
        )
        await self.session.commit()
        return EquipmentParameterReadingSubmitRead(
            reading=EquipmentParameterReadingRead.model_validate(reading),
            status=status,
            message=message,
        )
