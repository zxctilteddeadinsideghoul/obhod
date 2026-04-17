from app.repositories.admin import AdminRepository
from app.repositories.attachments import AttachmentsRepository
from app.repositories.checklists import ChecklistsRepository
from app.repositories.defects import DefectsRepository
from app.repositories.demo_data import DemoDataRepository
from app.repositories.equipment import EquipmentRepository
from app.repositories.rounds import RoundsRepository
from app.repositories.route_step_visits import RouteStepVisitsRepository
from app.repositories.routes import RoutesRepository
from app.repositories.tasks import TasksRepository

__all__ = [
    "AdminRepository",
    "AttachmentsRepository",
    "ChecklistsRepository",
    "DefectsRepository",
    "DemoDataRepository",
    "EquipmentRepository",
    "RoundsRepository",
    "RouteStepVisitsRepository",
    "RoutesRepository",
    "TasksRepository",
]
