from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import EquipmentRepository, RoundsRepository, RouteStepVisitsRepository
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
        rounds_repository: RoundsRepository,
        route_step_visits_repository: RouteStepVisitsRepository,
    ) -> None:
        self.session = session
        self.equipment_repository = equipment_repository
        self.rounds_repository = rounds_repository
        self.route_step_visits_repository = route_step_visits_repository

    async def execute(
        self,
        equipment_id: str,
        payload: EquipmentParameterReadingCreate,
        user_id: str,
    ) -> EquipmentParameterReadingSubmitRead:
        equipment = await self.equipment_repository.get(equipment_id)
        parameter_def = await self.equipment_repository.get_parameter_def(payload.parameter_def_id)
        if payload.route_step_id is None:
            raise ValueError("route_step_id is required")

        round_instance = await self.rounds_repository.get_by_route_step_and_employee(payload.route_step_id, user_id)
        await self.route_step_visits_repository.ensure_confirmed(round_instance, payload.route_step_id, equipment_id)
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
